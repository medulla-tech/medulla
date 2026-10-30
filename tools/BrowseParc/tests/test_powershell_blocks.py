#!/usr/bin/env python3
"""Validate every PowerShell block embedded in medulla-deploy-agent.sh.

Regression guard for a nasty bug: `pwsh -Command -` reads its input LINE BY
LINE, so a multi-line block (try/catch, scriptblock...) is never executed and
produces no output at all. ps_run() therefore folds the newlines away and sends
a single line; the blocks must stay valid PowerShell once folded.

Run:  python3 test_powershell_blocks.py
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = next((p for p in (os.path.join(HERE, "..", "server", "medulla-deploy-agent.sh"),
                           os.path.join(HERE, "..", "medulla-deploy-agent.sh"))
               if os.path.exists(p)), os.path.join(HERE, "..", "server", "medulla-deploy-agent.sh"))

FAILURES = []
CHECKS = [0]


def check(label, condition, detail=""):
    CHECKS[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s %s" % (label, detail))
        FAILURES.append(label)


def extract_blocks(source):
    """Every PS='...' / ps_script='...' block of the script, in order."""
    blocks = []
    for pattern in (r"PS='(.*?)'\n", r"ps_script='(.*?)'\n"):
        for match in re.finditer(pattern, source, re.S):
            blocks.append(match.group(1))
    return blocks


def parse_errors(pwsh, code):
    """PowerShell parse errors for the given code (nothing is executed)."""
    probe = (
        "$code = [Console]::In.ReadToEnd();"
        "$errors = $null;"
        "[System.Management.Automation.Language.Parser]::ParseInput($code, [ref]$null, [ref]$errors) | Out-Null;"
        "if ($errors) { $errors | ForEach-Object { $_.Message } } else { 'PARSE-OK' }"
    )
    proc = subprocess.run([pwsh, "-NoProfile", "-NonInteractive", "-Command", probe],
                          input=code.encode("utf-8"),
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.stdout.decode("utf-8", "replace")


def main():
    source = open(SCRIPT).read()
    blocks = extract_blocks(source)
    print("\n1. Blocs PowerShell presents dans le script")
    check("au moins 4 blocs extraits", len(blocks) >= 4, "trouve %d" % len(blocks))

    print("\n2. ps_run replie bien les sauts de ligne")
    ps_run_start = source.index("ps_run() {")
    ps_run_end = source.index("ps_json_parse_machines() {")
    ps_run_body = source[ps_run_start:ps_run_end]
    check("le repli 'tr' est present dans ps_run",
          "tr '\\n' ' '" in ps_run_body or 'tr "\\n" " "' in ps_run_body,
          ps_run_body[:400])
    check("le commentaire explique pourquoi",
          "LINE BY LINE" in ps_run_body or "ligne par ligne" in ps_run_body)

    pwsh = shutil.which("pwsh")
    if not pwsh:
        print("\n3. Validation PowerShell")
        print("  (pwsh absent du poste : verification de syntaxe ignoree)")
    else:
        print("\n3. Chaque bloc replie sur une ligne est du PowerShell valide")
        for index, block in enumerate(blocks):
            folded = " ".join(block.split("\n"))
            result = parse_errors(pwsh, folded)
            first_line = block.strip().split("\n")[0][:60]
            check("bloc %d valide (%s...)" % (index + 1, first_line),
                  "PARSE-OK" in result and "error" not in result.lower(),
                  result.strip()[:200])

        print("\n3 ter. Aucun commentaire '#' dans les blocs")
        # ps_run replie le bloc sur une seule ligne : un '#' commenterait tout ce
        # qui suit, accolade fermante comprise (panne silencieuse, sans reponse).
        for index, block in enumerate(blocks):
            check("bloc %d sans commentaire '#'" % (index + 1),
                  "#" not in block,
                  [line.strip() for line in block.split("\n") if "#" in line][:2])

            print("\n3 bis. Le script Windows genere pour l'agent choisi")
        # build_win_agent_ps construit le PowerShell a la volee : on l'execute
        # et on valide le resultat.
        bash = shutil.which("bash")
        if bash:
            gen = subprocess.run(
                [bash, "-c",
                 "eval \"$(sed -n '/^build_win_agent_ps() {/,/^}/p' %s)\"; "
                 "build_win_agent_ps 'https://exemple.invalid/medulla_agent/TAG/Medulla-Agent-windows-FULL-latest.exe' 'https://exemple.invalid/'" % SCRIPT],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            generated = gen.stdout.decode("utf-8", "replace").strip()
            check("script genere non vide", len(generated) > 40, repr(generated[:120]))
            check("script genere sur une seule ligne", "\n" not in generated, repr(generated[:200]))
            check("URL presente", "Medulla-Agent-windows-FULL-latest.exe" in generated)
            check("Referer present", generated.count("https://exemple.invalid/") >= 2)
            check("installation silencieuse /S", "/S" in generated)
            if generated:
                result = parse_errors(pwsh, generated)
                check("le script genere est du PowerShell valide",
                      "PARSE-OK" in result and "error" not in result.lower(),
                      result.strip()[:200])
        else:
            print("  (bash absent : test du script genere ignore)")

        print("\n4. Un bloc multi-ligne ne s'execute PAS (demonstration du bug)")
        multi = 'try {\n    "MULTILINE-OK"\n} catch {\n    "ERR"\n}\n'
        result = subprocess.run([pwsh, "-NoProfile", "-NonInteractive", "-Command", "-"],
                                input=multi.encode(), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT).stdout.decode("utf-8", "replace")
        check("le multi-ligne ne produit pas le resultat attendu",
              "MULTILINE-OK" not in result, repr(result[-80:]))
        single = 'try { "SINGLELINE-OK" } catch { "ERR" }'
        result = subprocess.run([pwsh, "-NoProfile", "-NonInteractive", "-Command", "-"],
                                input=(single + "\n").encode(), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT).stdout.decode("utf-8", "replace")
        check("la meme chose sur une ligne fonctionne", "SINGLELINE-OK" in result, repr(result[-80:]))

    print("\n=====================================")
    print("%d verifications, %d echec(s)" % (CHECKS[0], len(FAILURES)))
    if FAILURES:
        print("Echecs: %s" % ", ".join(FAILURES))
        return 1
    print("TOUS LES TESTS PASSENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
