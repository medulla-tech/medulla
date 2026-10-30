<#
    Medulla - Extraction des drivers et certificats vers le serveur via XMPP (v2)
    =============================================================================
    ExtractDrivers-XMPP.ps1

    VERSION 2 du package " Extract Drivers et Certificats " : le depot des
    drivers/certificats sur le serveur Medulla se fait par le PROTOCOLE XMPP
    (canal que l'agent utilise deja). Il n'y a AUCUN partage SMB et AUCUN
    identifiant de partage dans ce script : l'ancien compte de service et son
    mot de passe sont retires (et doivent etre changes cote serveur : le mot de
    passe a ete diffuse en clair dans l'ancienne version).

    Extraction (inchangee) :
      * pnputil (natif Microsoft) en methode par defaut, ddc.exe en secours ;
      * export TOUJOURS en local (disque systeme), jamais sur un lecteur reseau ;
      * regroupement des drivers par classe materielle (Class= de l'INF) ;
      * certificats TrustedPublisher nommes par Thumbprint (unique) ;
      * verification d'integrite avant tout envoi ;
      * journalisation persistante et codes de sortie distincts.

    Ce que la v2 ajoute :
      * envoi DIFFERENTIEL : le poste envoie d'abord un inventaire (empreinte de
        chaque package de drivers et de chaque certificat) ; le serveur ne
        demande que ce qui lui manque ou qui differe. Un depot deja a jour ne
        recoit rien (code 0, "rien a envoyer") ;
      * REPRISE : un transfert interrompu (coupure, redemarrage du poste ou du
        serveur) reprend au dernier bloc recu, sans tout renvoyer ;
      * un recepteur de production (server\plugin_extract_drivers.py) qui verifie
        tout avant d'ecrire dans le depot, et n'y supprime jamais rien ;
      * plus aucune archive complete construite sur le poste : seule l'archive
        differentielle l'est, et seulement si le serveur a besoin de quelque chose.

    Le contrat de depot et de protocole est decrit dans PROTOCOLE.md ; le
    transporteur Python reutilise le runtime et l'agentconf.ini de l'agent.

    Arborescence deposee sur le serveur (celle du partage historique, afin que
    l'injection de drivers a la masterisation continue de fonctionner) :
      <depot>\drivers\<OS>\<Fabricant>\<Modele>\DRIVERS\<Classe>\<package>\...
      <depot>\drivers\<OS>\<Fabricant>\<Modele>\CERTS\<Thumbprint>.cer

    Prerequis sur le poste
      * Windows 10/11 ou Windows Server, PowerShell 5.1+ ;
      * execution en administrateur local (verifie, sinon code 1) ;
      * agent Medulla installe et configure (fournit Python + agentconf.ini) ;
      * le module Send-DriversOverXmpp.py livre avec ce script ;
      * le plugin serveur plugin_extract_drivers.py installe sur le substitut maitre.

    Parametres (tous optionnels : le package fonctionne sans argument)
      -ExtractMethod       'pnp' (defaut) ou 'ddc' (Double Driver, legacy).
      -RemoteAction        Nom de l'action XMPP logique, c.-a-d. du plugin
                           recepteur cote substitut (defaut : extract_drivers).
      -MasterJid           JID du substitut recepteur (defaut : master@pulse).
      -AckMode             'required' (defaut), 'optional' ou 'none'. Ne concerne
                           que l'accuse de reception FINAL : le plan et la reprise
                           sont toujours negocies avec le serveur.
      -PlanTimeoutSeconds  Attente du plan du serveur apres l'inventaire
                           (defaut : 120).
      -ResumeTimeoutSeconds Attente de la reponse de reprise (defaut : 120).
      -AckTimeoutSeconds   Attente de l'accuse de reception final (defaut : 300).
      -ConnectTimeoutSeconds Delai de connexion/authentification (defaut : 30).
      -MaxRetries          Tentatives d'envoi (defaut : 3).
      -RetryDelaySeconds   Delai entre tentatives (defaut : 15).
      -SegmentBytes        Taille des blocs de l'archive (defaut : 25000,
                           bornes 1024-48000).
      -DelayMs             Pause supplementaire entre deux trames (defaut : 0,
                           la contre-pression est automatique).
      -TotalTimeoutSeconds Delai global du transfert (defaut : 3600).
      -CaCertPath          Bundle de CA a utiliser si la CA Medulla n'est pas
                           dans le magasin de confiance du poste. A renseigner
                           sur les postes hors domaine, sinon la verification
                           TLS par defaut peut faire echouer la connexion.
      -SkipTlsVerify       DESACTIVE la verification du certificat serveur
                           (diagnostic uniquement ; un avertissement est
                           journalise).
      -RequireStartTls     Exige une session chiffree, et echoue sinon.
      -ConfigSource        'auto' (defaut), 'agent' (JID fourni par la pile de
                           l'agent) ou 'minimal' (lecture de agentconf.ini).
      -XmppServer/-XmppPort Force le serveur/port XMPP (diagnostic).
      -PythonPath          Force l'interpreteur Python (defaut : celui de l'agent).
      -AgentConfPath       Force le chemin de agentconf.ini.
      -SenderScript        Force le chemin de Send-DriversOverXmpp.py.
      -CheckXmpp           Teste seulement la connexion XMPP puis quitte,
                           AVANT toute extraction (verifie aussi -RequireStartTls).
      -KeepStaging         Conserve le dossier de travail ET l'archive
                           differentielle (diagnostic), en succes comme en echec.
      -Verbose             Parametre commun PowerShell : journalisation
                           detaillee (transmis au transporteur XMPP).
      -DryRun              Simule l'extraction et l'envoi (aucune ecriture).

    Conservation des fichiers : le dossier de travail est toujours supprime en
    fin d'execution (sauf -KeepStaging). L'archive differentielle
    (extract-drivers-delta.zip) est supprimee apres un succes ; apres un echec
    elle est conservee pour analyse (ecrasee au passage suivant).

    Codes de sortie (convergence Medulla)
      0  Succes : depot mis a jour, OU deja a jour (rien a envoyer).
      1  Script non execute avec des droits administrateur.
      2  Prerequis manquant (agent Medulla absent, Python introuvable,
         agentconf.ini illisible, module d'envoi absent, metadonnees ou dossier
         de travail invalides).
      3  Echec de connexion ou d'authentification XMPP.
      4  Echec de l'extraction des drivers (pnputil/ddc en erreur, ou 0 fichier).
      5  Echec du transfert XMPP (pas de plan, de reprise ou d'accuse de
         reception du serveur, erreur renvoyee par le serveur, emission
         interrompue).
      99 Erreur inattendue non geree (voir extract-drivers.log).

    NB : les codes 2, 3 et 5 different de la version SMB (2 = serveur de depot
    introuvable, 3 = echec de mapping, 5 = echec de copie Robocopy). Penser a
    ajuster les regles de convergence si elles distinguaient les anciens codes.
#>

[CmdletBinding()]
param(
    [ValidateSet("pnp", "ddc")]
    [string]$ExtractMethod = "pnp",

    [string]$RemoteAction = "extract_drivers",

    [string]$MasterJid = "master@pulse",

    # "required" par defaut : un succes ne doit pas pouvoir etre confondu avec
    # un transfert parti dans le vide. Passer -AckMode optional tant que le
    # recepteur serveur n'acquitte pas encore.
    [ValidateSet("optional", "required", "none")]
    [string]$AckMode = "required",

    [ValidateRange(1, 3600)]
    [int]$PlanTimeoutSeconds    = 120,
    [ValidateRange(1, 3600)]
    [int]$ResumeTimeoutSeconds  = 120,
    [ValidateRange(1, 86400)]
    [int]$AckTimeoutSeconds     = 300,
    [ValidateRange(1, 3600)]
    [int]$ConnectTimeoutSeconds = 30,
    [ValidateRange(1, 20)]
    [int]$MaxRetries            = 3,
    [ValidateRange(1, 3600)]
    [int]$RetryDelaySeconds     = 15,
    # Memes bornes que le transporteur (sous peine d'un refus en code 2).
    [ValidateRange(1024, 48000)]
    [int]$SegmentBytes          = 25000,
    [ValidateRange(0, 10000)]
    [int]$DelayMs               = 0,
    [ValidateRange(60, 86400)]
    [int]$TotalTimeoutSeconds   = 3600,

    [string]$CaCertPath    = "",
    [ValidateSet("auto", "agent", "minimal")]
    [string]$ConfigSource  = "auto",
    [string]$XmppServer    = "",
    [int]$XmppPort         = 0,

    [string]$PythonPath    = "",
    [string]$AgentConfPath = "",
    [string]$SenderScript  = "",

    [switch]$SkipTlsVerify,
    [switch]$RequireStartTls,
    [switch]$CheckXmpp,
    [switch]$KeepStaging,
    # NB : pas de [switch]$Verbose ici. [CmdletBinding()] fournit deja le
    # parametre commun -Verbose (variable $VerbosePreference) ; le redeclarer
    # fait echouer le script des la liaison des parametres ("A parameter with
    # the name 'Verbose' was defined multiple times").
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# --- Constantes -----------------------------------------------------------
$LogDir      = "C:\ProgramData\Medulla\ExtractDrivers"
$LogFile     = Join-Path $LogDir "extract-drivers.log"
$SenderLog   = Join-Path $LogDir "xmpp-send.log"
$SenderConsoleLog = Join-Path $LogDir "xmpp-console.log"
$SenderResult = Join-Path $LogDir "xmpp-result.json"
$StagingRoot = Join-Path $LogDir "staging"
$MetadataFile = Join-Path $StagingRoot "metadata.json"
$ArchivePath = Join-Path $LogDir "extract-drivers-delta.zip"

New-Item -ItemType Directory -Force -Path $LogDir -ErrorAction SilentlyContinue | Out-Null

$ExitCode = 99

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR")]
        [string]$Level = "INFO"
    )
    $line = "{0} - [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level, $Message
    # L'ecriture du journal ne doit JAMAIS faire echouer le script (disque plein,
    # fichier verrouille par une execution concurrente, droits...) : sinon
    # $ErrorActionPreference = "Stop" ferait sortir le script sans code de
    # sortie exploitable. On retombe alors sur la console seule.
    try {
        Add-Content -Path $LogFile -Value $line -ErrorAction Stop
    } catch {
        [Console]::WriteLine("$line (journal non inscriptible : $($_.Exception.Message))")
    }
    # [Console]::WriteLine (plutot que Write-Output) : reste visible dans la
    # sortie capturee par Medulla sans polluer la valeur de retour des
    # fonctions qui appellent Write-Log.
    [Console]::WriteLine($line)
}

function Get-InfDeviceClass {
    # Lit la valeur Class= de la section [Version] d'un .inf pour regrouper
    # les drivers exportes par type de materiel (Net, Media, Printer, etc.).
    param([string]$InfPath)
    $inVersionSection = $false
    foreach ($line in Get-Content -Path $InfPath -ErrorAction SilentlyContinue) {
        $trimmed = $line.Trim()
        if ($trimmed -match '^\[Version\]$') { $inVersionSection = $true; continue }
        if ($trimmed -match '^\[.+\]$') { $inVersionSection = $false; continue }
        if ($inVersionSection -and $trimmed -match '^Class\s*=\s*([^;]+)') {
            return $Matches[1].Trim().Trim('"')
        }
    }
    return "Autre"
}

function Test-PlaceholderName {
    # Valeurs bidons laissees par certains constructeurs de cartes meres
    # (ex. "Default string", "System Product Name", "To Be Filled By O.E.M.").
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $true }
    $norm = ($Value.Trim().ToLowerInvariant() -replace '[\s\._-]+', ' ').Trim()
    $placeholders = @(
        'default string', 'system product name', 'system manufacturer',
        'system version', 'to be filled by o e m', 'to be filled by oem',
        'o e m', 'oem', 'not applicable', 'not specified', 'unknown', 'none',
        'n a', 'na', 'type1productconfigid', 'default'
    )
    return ($placeholders -contains $norm)
}

function Resolve-HardwareName {
    # Premier candidat non bidon, sinon "Inconnu".
    param([string[]]$Candidates)
    foreach ($c in $Candidates) {
        if (-not (Test-PlaceholderName -Value $c)) { return $c.Trim() }
    }
    return "Inconnu"
}

function Resolve-PythonPath {
    # L'agent Medulla embarque son propre Python : on reutilise celui-la, car
    # c'est le seul dont on sait qu'il dispose de slixmpp et du paquet
    # pulse_xmpp_agent (indispensable pour reprendre l'identite XMPP).
    param([string]$Forced)
    if (-not [string]::IsNullOrWhiteSpace($Forced)) {
        if (Test-Path -LiteralPath $Forced) { return (Resolve-Path -LiteralPath $Forced).Path }
        throw "PythonPath fourni introuvable : $Forced"
    }
    # NB : on ne construit un chemin qu'avec des racines reellement definies
    # (`${env:ProgramFiles(x86)}` est vide sur un hote 32 bits, et Join-Path
    # leve alors une erreur de liaison de parametre).
    $roots = @($env:ProgramFiles, ${env:ProgramFiles(x86)}, "C:\") |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    $candidates = @()
    foreach ($root in $roots) {
        foreach ($sub in @("Python3", "Python311", "Python310", "Python39")) {
            $candidates += (Join-Path $root "$sub\python.exe")
        }
    }
    $candidates += "C:\Python3\python.exe"
    # @() : un seul resultat serait sinon une chaine, et $candidates[0] son 1er caractere.
    $candidates = @($candidates | Where-Object { Test-Path -LiteralPath $_ })

    if ($candidates.Count -gt 0) { return $candidates[0] }

    $onPath = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($onPath) { return $onPath.Source }
    return $null
}

function Resolve-SenderScript {
    # Le flux Medulla copie le PACKAGE dans un dossier UID et positionne le
    # repertoire courant dessus : le module peut donc se trouver a cote du
    # script, dans le repertoire courant, ou dans le dossier de travail.
    param([string]$Forced)
    $candidates = @()
    if (-not [string]::IsNullOrWhiteSpace($Forced)) { $candidates += $Forced }
    $candidates += @(
        (Join-Path (Get-Location).Path "Send-DriversOverXmpp.py"),
        (Join-Path $PSScriptRoot "Send-DriversOverXmpp.py"),
        (Join-Path $LogDir "Send-DriversOverXmpp.py")
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    return $null
}

function Invoke-NativeCaptured {
    # Execute un programme natif en redirigeant TOUS ses flux vers un fichier,
    # puis journalise la fin de cette sortie. Retourne son code de sortie.
    #
    # Pourquoi ne pas utiliser `& outil 2>&1 | ForEach-Object { ... }` : sous
    # Windows PowerShell 5.1, la sortie d'erreur d'un programme natif remontee
    # dans le pipeline devient des ErrorRecord qui, avec
    # $ErrorActionPreference = "Stop", font echouer le script. C'est
    # exactement le piege qui faisait sortir le script en 99 au lieu de 4.
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [string[]]$Arguments = @(),
        [string]$Tag = "outil"
    )
    $capture = Join-Path $LogDir "$Tag-console.log"
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Executable @Arguments *> $capture
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    if (Test-Path -LiteralPath $capture) {
        foreach ($line in @(Get-Content -LiteralPath $capture -Tail 30 -Encoding UTF8 `
                    -ErrorAction SilentlyContinue)) {
            Write-Log "${Tag}: $line"
        }
    }
    return $code
}

function Invoke-XmppSender {
    # Appelle Send-DriversOverXmpp.py et retourne son code de sortie.
    # Les arguments sont passes sous forme de tableau (splatting) : PowerShell
    # se charge de l'echappement des chemins contenant des espaces, on
    # n'insere donc AUCUN guillemet dans les valeurs.
    param(
        [string]$Python,
        [string]$SenderModule,
        [string]$Staging  = "",
        [string]$Metadata = "",
        [switch]$CheckOnly
    )
    $arguments = New-Object System.Collections.Generic.List[string]
    $arguments.Add($SenderModule)
    if (-not [string]::IsNullOrWhiteSpace($Staging)) {
        $arguments.Add("--staging");   $arguments.Add($Staging)
        $arguments.Add("--delta-zip"); $arguments.Add($ArchivePath)
    }
    if (-not [string]::IsNullOrWhiteSpace($Metadata)) {
        $arguments.Add("--metadata"); $arguments.Add($Metadata)
    }
    $arguments.Add("--action");          $arguments.Add($RemoteAction)
    $arguments.Add("--master-jid");      $arguments.Add($MasterJid)
    $arguments.Add("--ack-mode");        $arguments.Add($AckMode)
    $arguments.Add("--plan-timeout");    $arguments.Add("$PlanTimeoutSeconds")
    $arguments.Add("--resume-timeout");  $arguments.Add("$ResumeTimeoutSeconds")
    $arguments.Add("--ack-timeout");     $arguments.Add("$AckTimeoutSeconds")
    $arguments.Add("--connect-timeout"); $arguments.Add("$ConnectTimeoutSeconds")
    $arguments.Add("--max-retries");     $arguments.Add("$MaxRetries")
    $arguments.Add("--retry-delay");     $arguments.Add("$RetryDelaySeconds")
    $arguments.Add("--segment-bytes");   $arguments.Add("$SegmentBytes")
    $arguments.Add("--delay-ms");        $arguments.Add("$DelayMs")
    $arguments.Add("--total-timeout");   $arguments.Add("$TotalTimeoutSeconds")
    $arguments.Add("--config-source");   $arguments.Add($ConfigSource)
    $arguments.Add("--log");             $arguments.Add($SenderLog)
    $arguments.Add("--result");          $arguments.Add($SenderResult)
    if (-not [string]::IsNullOrWhiteSpace($AgentConfPath)) {
        $arguments.Add("--config"); $arguments.Add($AgentConfPath)
    }
    if (-not [string]::IsNullOrWhiteSpace($CaCertPath)) {
        $arguments.Add("--ca-cert"); $arguments.Add($CaCertPath)
    }
    if (-not [string]::IsNullOrWhiteSpace($XmppServer)) {
        $arguments.Add("--server"); $arguments.Add($XmppServer)
    }
    if ($XmppPort -gt 0) {
        $arguments.Add("--port"); $arguments.Add("$XmppPort")
    }
    if ($SkipTlsVerify)   { $arguments.Add("--tls-verify"); $arguments.Add("0") }
    if ($RequireStartTls) { $arguments.Add("--require-starttls") }
    if ($CheckOnly)       { $arguments.Add("--check") }
    if ($KeepStaging)     { $arguments.Add("--keep-archive") }
    # $VerbosePreference est alimente par le parametre commun -Verbose.
    if ($VerbosePreference -ne "SilentlyContinue") { $arguments.Add("--verbose") }

    Write-Log ("Appel du transporteur XMPP : {0} {1}" -f $Python, ($arguments -join ' '))

    # Redirection de TOUS les flux vers un fichier plutot que `2>&1 | ...` :
    # sous Windows PowerShell 5.1, la sortie d'erreur d'un programme natif
    # remontee dans le pipeline produit des ErrorRecord qui, avec
    # $ErrorActionPreference = "Stop", interrompent le script -- or le
    # transporteur journalise (beaucoup) sur stderr.
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Python @($arguments) *> $SenderConsoleLog
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    # On ne recopie que la fin de la sortie du transporteur (le detail complet
    # est dans $SenderLog, ecrit par le transporteur lui-meme).
    if (Test-Path -LiteralPath $SenderConsoleLog) {
        $tail = Get-Content -LiteralPath $SenderConsoleLog -Tail 40 -Encoding UTF8 `
            -ErrorAction SilentlyContinue
        foreach ($line in $tail) { Write-Log "xmpp: $line" }
    }
    return $exitCode
}

function Get-SenderResult {
    # Lit le resultat JSON produit par le transporteur (facultatif : si le
    # fichier est absent, on se contente du code de sortie).
    if (-not (Test-Path -LiteralPath $SenderResult)) { return $null }
    try {
        return Get-Content -LiteralPath $SenderResult -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        Write-Log "Resultat XMPP illisible ($SenderResult) : $($_.Exception.Message)" "WARN"
        return $null
    }
}

Write-Log "=== Extraction drivers et certificats (XMPP) : debut ==="

try {
    # --- Verification des privileges administrateur -----------------------
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal(
        [Security.Principal.WindowsIdentity]::GetCurrent()
    )
    if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Log "Le script doit etre execute avec des droits administrateur." "ERROR"
        $ExitCode = 1
        exit $ExitCode
    }
    if (-not $DryRun) {
        # --- Prerequis : Python de l'agent + module d'envoi ---------------
        $Python = Resolve-PythonPath -Forced $PythonPath
        if (-not $Python) {
            Write-Log "Python de l'agent Medulla introuvable. L'agent est-il installe sur ce poste ? Utiliser -PythonPath pour forcer l'interpreteur." "ERROR"
            $ExitCode = 2
            exit $ExitCode
        }
        Write-Log "Interpreteur Python : $Python"

        $SenderModule = Resolve-SenderScript -Forced $SenderScript
        if (-not $SenderModule) {
            Write-Log "Module Send-DriversOverXmpp.py introuvable (a cote du script, dans le repertoire courant du package, ou dans $LogDir)." "ERROR"
            $ExitCode = 2
            exit $ExitCode
        }
        Write-Log "Transporteur XMPP : $SenderModule"

        # --- Test de connexion XMPP seul (-CheckXmpp) --------------------
        # Volontairement place AVANT toute extraction : " tester la connexion "
        # ne doit ni exporter les drivers, ni construire une archive de
        # plusieurs Go, ni masquer un verdict de connexion par un code 4 lie a
        # l'extraction.
        if ($CheckXmpp) {
            if (Test-Path -LiteralPath $SenderResult) { Remove-Item -LiteralPath $SenderResult -Force }
            $senderExit = Invoke-XmppSender -Python $Python -SenderModule $SenderModule -CheckOnly
            $senderResult = Get-SenderResult
            if ($senderExit -eq 0) {
                Write-Log "Test de connexion XMPP reussi (JID : $($senderResult.jid))."
                Write-Log "=== Extraction drivers et certificats (XMPP) : test XMPP OK ==="
                $ExitCode = 0
            } else {
                Write-Log "Test de connexion XMPP en echec (code transporteur $senderExit, voir $SenderLog)." "ERROR"
                $ExitCode = if ($senderExit -eq 2) { 2 } elseif ($senderExit -eq 3) { 3 } elseif ($senderExit -eq 99) { 99 } else { 5 }
            }
            exit $ExitCode
        }

        # --- Informations machine ----------------------------------------
        $os     = Get-CimInstance -ClassName Win32_OperatingSystem
        $system = Get-CimInstance -ClassName Win32_ComputerSystem
        $bios   = Get-CimInstance -ClassName Win32_BIOS
        $board  = Get-CimInstance -ClassName Win32_BaseBoard -ErrorAction SilentlyContinue
        $product = Get-CimInstance -ClassName Win32_ComputerSystemProduct -ErrorAction SilentlyContinue

        $osParts        = $os.Caption -split ' '
        $WINDOWS_FOLDER = ($osParts | Select-Object -Skip 1 -First 2) -join ''
        # Fabricant/modele : ComputerSystem, puis carte mere (et BIOS pour le
        # fabricant) quand le constructeur a laisse une valeur bidon.
        $MANUF_NAME     = Resolve-HardwareName -Candidates @($system.Manufacturer, $board.Manufacturer, $bios.Manufacturer)
        $MODEL_NAME     = Resolve-HardwareName -Candidates @($system.Model, $board.Product, $product.Name, $product.Version, $system.SystemSKUNumber, $board.Version)
        if ($MODEL_NAME -eq "Inconnu" -and -not (Test-PlaceholderName -Value $bios.SMBIOSBIOSVersion)) {
            # Dernier recours : la version du BIOS evite de melanger des cartes differentes.
            $MODEL_NAME = "Inconnu BIOS-$($bios.SMBIOSBIOSVersion.Trim())"
        }
        $MANUF          = (($MANUF_NAME -replace '[\s\.]', '') -replace '[\\/:*?"<>|]', '_')
        $MODEL          = (($MODEL_NAME -replace '\s', '_') -replace '[\\/:*?"<>|]', '_')
        $SERIAL         = ($bios.SerialNumber -replace '[\\/:*?"<>|\s]', '')

        Write-Log "OS=$WINDOWS_FOLDER Fabricant=$MANUF Modele=$MODEL Serie=$SERIAL Hote=$($env:COMPUTERNAME)"
        Write-Log "Action XMPP=$RemoteAction Destinataire=$MasterJid ACK=$AckMode"

        # --- Dossier de travail (local, jamais sur le reseau) ------------
        $BaseDir   = Join-Path $StagingRoot "$WINDOWS_FOLDER\$MANUF\$MODEL"
        $DriverDir = Join-Path $BaseDir "DRIVERS"
        $CertDir   = Join-Path $BaseDir "CERTS"

        if (Test-Path -LiteralPath $StagingRoot) {
            Remove-Item -LiteralPath $StagingRoot -Recurse -Force
        }
        New-Item -ItemType Directory -Force -Path $DriverDir | Out-Null
        New-Item -ItemType Directory -Force -Path $CertDir   | Out-Null

        # --- Extraction des drivers --------------------------------------
        $driverExportOk = $false
        if ($ExtractMethod -eq "ddc") {
            # Le flux Medulla copie le PACKAGE (conf.json, xmppdeploy.json,
            # binaire) dans un dossier UID et positionne le repertoire courant
            # dessus (etape "action_pwd_package") : ddc.exe, s'il est bundle
            # dans le package, est donc trouve via le repertoire courant.
            $ddcCandidates = @(
                (Join-Path (Get-Location).Path "ddc.exe"),
                (Join-Path $PSScriptRoot "ddc.exe"),
                (Join-Path $LogDir "ddc.exe")
            )
            $ddcPath = $ddcCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
            if (-not $ddcPath) {
                Write-Log "ddc.exe introuvable ($($ddcCandidates -join ', ')), bascule automatique sur pnputil." "WARN"
                $ExtractMethod = "pnp"
            } else {
                Write-Log "ddc.exe trouve : $ddcPath"
                # Voir la note de Invoke-XMPP-Sender : sous Windows PowerShell
                # 5.1, `2>&1 | ...` sur un programme natif produit des
                # ErrorRecord qui, avec $ErrorActionPreference = "Stop",
                # interrompent le script (et feraient sauter le repli sur
                # pnputil). On redirige donc vers un fichier, avec
                # ErrorActionPreference temporairement permissif.
                $driverExportOk = (Invoke-NativeCaptured -Executable $ddcPath `
                        -Arguments @("b", "/target:$DriverDir") -Tag "ddc") -eq 0
            }
        }

        if ($ExtractMethod -eq "pnp") {
            $driverExportOk = (Invoke-NativeCaptured `
                    -Executable "$env:WINDIR\System32\pnputil.exe" `
                    -Arguments @("/export-driver", "*", $DriverDir) -Tag "pnputil") -eq 0
        }

        # --- Regroupement des drivers par type de materiel ---------------
        $pkgDirs = Get-ChildItem -Path $DriverDir -Directory -ErrorAction SilentlyContinue
        foreach ($pkgDir in $pkgDirs) {
            $infFile = Get-ChildItem -Path $pkgDir.FullName -Filter "*.inf" -File -ErrorAction SilentlyContinue |
                Select-Object -First 1
            $deviceClass = if ($infFile) { Get-InfDeviceClass -InfPath $infFile.FullName } else { "Autre" }
            $deviceClass = ($deviceClass -replace '[\\/:*?"<>|]', '_').Trim()
            if ([string]::IsNullOrWhiteSpace($deviceClass)) { $deviceClass = "Autre" }
            $classDir = Join-Path $DriverDir $deviceClass
            New-Item -ItemType Directory -Force -Path $classDir | Out-Null
            Move-Item -LiteralPath $pkgDir.FullName -Destination (Join-Path $classDir $pkgDir.Name) -Force
        }
        if ($pkgDirs) {
            Write-Log "Drivers regroupes par type de materiel sous $DriverDir."
        }

        $exportedDriverCount = (Get-ChildItem -Path $DriverDir -Filter "*.inf" -Recurse -ErrorAction SilentlyContinue).Count
        Write-Log "Drivers exportes localement : $exportedDriverCount fichier(s) .inf (code retour export : $driverExportOk)."

        if (-not $driverExportOk -or $exportedDriverCount -eq 0) {
            Write-Log "Echec de l'extraction des drivers (methode=$ExtractMethod)." "ERROR"
            $ExitCode = 4
            exit $ExitCode
        }

        # --- Extraction des certificats (nommage par Thumbprint) ---------
        $certsToExport = @(Get-ChildItem -Path Cert:\LocalMachine\TrustedPublisher -ErrorAction SilentlyContinue)
        $exportedCertCount = 0
        foreach ($cert in $certsToExport) {
            $certFileName = "$($cert.Thumbprint).cer"
            $certFilePath = Join-Path $CertDir $certFileName
            [IO.File]::WriteAllBytes($certFilePath, $cert.Export("Cert"))
            $exportedCertCount++
        }
        Write-Log "Certificats TrustedPublisher exportes : $exportedCertCount / $($certsToExport.Count)."

        # --- Metadonnees (transmises dans l'inventaire et l'archive) -----
        $metadata = [ordered]@{
            schema         = "medulla.extractdrivers.v2"
            collected_at   = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            hostname       = $env:COMPUTERNAME
            os             = $WINDOWS_FOLDER
            os_caption     = $os.Caption
            manufacturer   = $MANUF_NAME
            manufacturer_raw = $system.Manufacturer
            manufacturer_dir = $MANUF
            model          = $MODEL_NAME
            model_raw      = $system.Model
            model_dir      = $MODEL
            serial         = $SERIAL
            relative_dir   = "$WINDOWS_FOLDER/$MANUF/$MODEL"
            depot_subdir   = "drivers"
            extract_method = $ExtractMethod
            drivers_count  = $exportedDriverCount
            certs_count    = $exportedCertCount
        }
        $metadataJson = $metadata | ConvertTo-Json -Depth 4
        # UTF-8 sans BOM : le transporteur lit ce fichier avec json.load().
        [IO.File]::WriteAllText($MetadataFile, $metadataJson, (New-Object Text.UTF8Encoding($false)))
        Write-Log "Metadonnees ecrites : $MetadataFile"

        # --- Transfert XMPP ---------------------------------------------
        if (Test-Path -LiteralPath $SenderResult) { Remove-Item -LiteralPath $SenderResult -Force }
        # Le transporteur inventorie le dossier de travail, negocie un plan avec
        # le serveur, et ne construit l'archive differentielle que si besoin.
        $senderExit = Invoke-XmppSender -Python $Python -SenderModule $SenderModule -Staging $StagingRoot -Metadata $MetadataFile
        $senderResult = Get-SenderResult

        if ($senderResult) {
            Write-Log ("Resultat XMPP : status={0} session={1} trames={2} confirme={3}" -f `
                $senderResult.status, $senderResult.sessionid,
                $senderResult.frames_sent, $senderResult.confirmed)
            if ($senderResult.nothing_to_send) {
                Write-Log "Le serveur est deja a jour : aucune donnee a envoyer."
            } else {
                Write-Log ("Envoye : {0} package(s) et {1} certificat(s) ; deja presents : {2} package(s), {3} certificat(s) ; reprise au bloc {4}." -f `
                    $senderResult.packages_sent, $senderResult.certs_sent,
                    $senderResult.packages_skipped, $senderResult.certs_skipped,
                    $senderResult.resumed_from_block)
            }
        }

        switch ($senderExit) {
            0 {
                if ($senderResult -and -not $senderResult.confirmed) {
                    Write-Log "Transfert emis vers $MasterJid mais SANS accuse de reception du serveur (mode $AckMode)." "WARN"
                } else {
                    Write-Log "Transfert XMPP confirme par le serveur."
                }
                Write-Log "Extraction et depot termines : $exportedDriverCount driver(s), $exportedCertCount certificat(s) extraits -> $MasterJid (action $RemoteAction)."
                Write-Log "=== Extraction drivers et certificats (XMPP) : succes ==="
                $ExitCode = 0
            }
            2 {
                Write-Log "Prerequis du transporteur XMPP non satisfait (voir $SenderLog)." "ERROR"
                $ExitCode = 2
            }
            3 {
                Write-Log "Connexion ou authentification XMPP impossible (voir $SenderLog)." "ERROR"
                $ExitCode = 3
            }
            99 {
                Write-Log "Erreur inattendue du transporteur XMPP (code 99, voir $SenderLog)." "ERROR"
                $ExitCode = 99
            }
            default {
                Write-Log "Echec du transfert XMPP (code transporteur $senderExit, voir $SenderLog)." "ERROR"
                $ExitCode = 5
            }
        }
    }
    else {
        # --- Mode simulation ---------------------------------------------
        Write-Log "[DRY-RUN] Aucune extraction ni transfert reel."
        Write-Log "[DRY-RUN] Archive differentielle (si le serveur en demande une) : $ArchivePath"
        Write-Log "[DRY-RUN] Commande : (Python de l'agent) Send-DriversOverXmpp.py --staging <dossier de travail> --action $RemoteAction --master-jid $MasterJid"
        Write-Log "=== Extraction drivers et certificats (XMPP) : succes (dry-run) ==="
        $ExitCode = 0
    }
}
catch {
    # Filet de securite : toute erreur non geree est journalisee clairement au
    # lieu de remonter un code de sortie ambigu (confondu avec le controle
    # d'administrateur).
    Write-Log "Erreur inattendue : $($_.Exception.Message)" "ERROR"
    $ExitCode = 99
}
finally {
    # Nettoyage : rien n'est supprime hors du dossier de travail et de
    # l'archive differentielle (aucune suppression destructive ailleurs).
    if (-not $KeepStaging) {
        if (Test-Path -LiteralPath $StagingRoot) {
            Remove-Item -LiteralPath $StagingRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $ArchivePath) {
            if ($ExitCode -eq 0) {
                Remove-Item -LiteralPath $ArchivePath -Force -ErrorAction SilentlyContinue
            } else {
                # Echec : l'archive differentielle est conservee pour analyse. Le
                # serveur reprend de toute facon un transfert interrompu (l'archive
                # est deterministe, donc de meme empreinte au passage suivant) ; le
                # nom fixe borne la consommation disque a une archive.
                Write-Log "Archive differentielle conservee apres echec : $ArchivePath (ecrasee au prochain passage)." "WARN"
            }
        }
    } else {
        Write-Log "KeepStaging : dossier de travail conserve dans $StagingRoot."
    }
    Write-Log "=== Fin du script (code de sortie $ExitCode) ==="
}

exit $ExitCode
