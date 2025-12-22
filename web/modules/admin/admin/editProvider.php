<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: editProvider.php
 */
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
?>
<style>
#Form > table{
  width:100% !important;
  margin:0 auto !important;
  border-collapse:separate;
  border-spacing:0;
  margin-top:1.5rem !important;
}

#Form tr > td.label{
  width:28% !important;
  text-align:right;
  padding-right:0;
}

#Form tr > td.label + td{
  padding-left:3rem !important;
  vertical-align:middle;
}

#Form tr > td.label + td span[id^="container_input_"]{
  display:inline-block;
  position:relative;
  width:32rem;
  max-width:100%;
}

#Form tr > td.label + td span[id^="container_input_"] > input[type="text"],
#Form tr > td.label + td span[id^="container_input_"] > input[type="password"],
#Form tr > td.label + td span[id^="container_input_"] > input:not([type]){
  width:100%;
  box-sizing:border-box;
}

#Form tr > td.label + td .pw-wrap{
  position:relative; display:inline-block; width:100%;
}
#Form tr > td.label + td .pw-wrap > input{
  padding-right:2.2rem;
}
#Form tr > td.label + td .pw-toggle{
  position:absolute; right:.6rem; top:50%; transform:translateY(-50%);
  width:1.1rem; height:1.1rem; border:0; background:transparent; padding:0; cursor:pointer;
  line-height:1; z-index:2;
}
#Form tr > td.label + td .pw-toggle img{
  width:100%; height:100%; display:block; pointer-events:none;
}

#Form .btn, #Form .btnPrimary,
#Form input[type="submit"], #Form input[type="button"], #Form input[type="reset"]{
  width:auto !important;
}
</style>

<?php
$safe   = fn($v) => htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8');
$isRoot = (strcasecmp($_SESSION['login'] ?? '', 'root') === 0);

$mode   = (strtolower($_GET['mode'] ?? '') === 'edit') ? 'edit' : 'add';
$name   = trim((string)($_GET['name'] ?? ''));
$client = (string)($_GET['client'] ?? ($_SESSION['o'] ?? 'MMC'));

// Pre-sealing
$prefill = [
    'id'             => '',
    'client_name'    => $client,
    'name'           => $name,
    'logo_url'       => '',
    'url_provider'   => '',
    'client_id'      => '',
    'client_secret'  => '',
    'ldap_uid'       => '',
    'ldap_givenName' => '',
    'ldap_sn'        => '',
    'ldap_mail'      => '',
    'proxy_url'      => '',
    // to activate later:
    // 'profiles_order' => '',
    // 'acls_json'      => '',
];

// CREATE
if (isset($_POST['bcreate'])) {
    $data = [
        'client_name'    => $_POST['client_name']    ?? 'MMC',
        'name'           => $_POST['name']           ?? '',
        'logo_url'       => $_POST['logo_url']       ?? '',
        'url_provider'   => $_POST['url_provider']   ?? '',
        'client_id'      => $_POST['client_id']      ?? '',
        'client_secret'  => $_POST['client_secret']  ?? '',

        // Optional → Defaults side SQL/Python if empty
        'ldap_uid'       => $_POST['ldap_uid']       ?? null,
        'ldap_givenName' => $_POST['ldap_givenName'] ?? null,
        'ldap_sn'        => $_POST['ldap_sn']        ?? null,
        'ldap_mail'      => $_POST['ldap_mail']      ?? null,
        'proxy_url'      => $_POST['proxy_url']      ?? null,

        // to activate later:
        // 'profiles_order' => $_POST['profiles_order'] ?? null,
        // 'acls_json'      => $_POST['acls_json']      ?? null,
    ];

    try {
        $res = xmlrpc_create_provider($data);
        if (!empty($res['ok'])) {
            new NotifyWidgetSuccess(_T("Provider created successfully", "admin"));
            header("Location: " . urlStrRedirect("admin/admin/manageproviders", []));
            exit;
        }
        throw new Exception($res['error'] ?? 'Unknown error');
    } catch (Exception $e) {
        new NotifyWidgetFailure(_T("Creation failed: ", "admin") . $safe($e->getMessage()));
    }
}

// UPDATE
if (isset($_POST['bupdate'])) {
    $data = [
        'id'             => $_POST['id']             ?? null,
        'logo_url'       => $_POST['logo_url']       ?? null,
        'url_provider'   => $_POST['url_provider']   ?? null,
        'client_id'      => $_POST['client_id']      ?? null,
        // empty secret => we do not modify
        'client_secret'  => (($_POST['client_secret'] ?? '') !== '') ? $_POST['client_secret'] : null,

        'ldap_uid'       => $_POST['ldap_uid']       ?? null,
        'ldap_givenName' => $_POST['ldap_givenName'] ?? null,
        'ldap_sn'        => $_POST['ldap_sn']        ?? null,
        'ldap_mail'      => $_POST['ldap_mail']      ?? null,
        'proxy_url'      => $_POST['proxy_url']      ?? null,

        // to activate later:
        // 'lmc_acl'        => $_POST['lmc_acl']        ?? null,
        // 'profiles_order' => $_POST['profiles_order'] ?? null,
        // 'acls_json'      => $_POST['acls_json']      ?? null,
    ];

    if ($isRoot && isset($_POST['client_name'])) {
        $data['client_name'] = $_POST['client_name'];
    }

    try {
        $res = xmlrpc_update_provider($data);
        if (!empty($res['ok'])) {
            new NotifyWidgetSuccess(_T("Provider updated successfully", "admin"));
            header("Location: " . urlStrRedirect("admin/admin/manageproviders", []));
            exit;
        }
        throw new Exception($res['error'] ?? 'Unknown error');
    } catch (Exception $e) {
        new NotifyWidgetFailure(_T("Update failed: ", "admin") . $safe($e->getMessage()));
    }
}

if ($mode === 'edit' && $name !== '') {
    $all = xmlrpc_get_providers($_SESSION['login'] ?? '', $client);
    foreach ($all as $p) {
        if (($p['name'] ?? '') === $name) {
            $prefill = array_merge($prefill, $p);
            break;
        }
    }
}

// Title
$title = ($mode === 'edit')
    ? sprintf(_T("Edit provider <span style='font-size: 16px;'>[%s]</span>", 'admin'), $safe($prefill['name']))
    : _T("Add a new provider", 'admin');

$page = new PageGenerator("<h2>{$title}</h2>");
$page->setSideMenu($sidemenu);
$page->display();

$submitName  = ($mode === 'edit') ? 'bupdate' : 'bcreate';
$submitLabel = ($mode === 'edit') ? _T("Save changes", "admin") : _T("Create provider", "admin");

$form = new ValidatingForm(['method' => 'POST']);
$form->addValidateButtonWithValue($submitName, $submitLabel);
$form->push(new Table());

// customer: editable only for root
if ($isRoot) {
    $form->add(
        new TrFormElement(_T("Client", "admin"), new InputTpl('client_name', '/^[A-Za-z0-9._\- ]{1,64}$/')),
        ['value' => $prefill['client_name']]
    );
} else {
    $form->add(new TrFormElement(_T("Client", "admin"), new TextTpl($safe($prefill['client_name']))));
    $form->add(new HiddenTpl('client_name'), ['value' => (string)$prefill['client_name'], 'hide' => true]);
}

// Provider name
if ($mode === 'edit') {
    $form->add(new TrFormElement(_T("Provider name", "admin"), new TextTpl($safe($prefill['name']))));
    $form->add(new HiddenTpl('name'), ['value' => (string)$prefill['name'], 'hide' => true]);
} else {
    $form->add(
        new TrFormElement(_T("Provider name", "admin"), new InputTpl('name', '/^[A-Za-z0-9._\- ]{1,64}$/')),
        ['value' => $_POST['name'] ?? '']
    );
}

$form->add(new TrFormElement(_T("Logo URL", "admin"),    new InputTpl('logo_url', '/^.{0,400}$/')),     ['value' => $prefill['logo_url']]);
$form->add(new TrFormElement(_T("Issuer URL", "admin"),  new InputTpl('url_provider', '/^.{1,400}$/')), ['value' => $prefill['url_provider']]);
$form->add(new TrFormElement(_T("Client ID", "admin"),   new InputTpl('client_id', '/^.{1,400}$/')),    ['value' => $prefill['client_id']]);

// secret: if not modify keep current
$secretInput = ($mode === 'edit')
  ? new InputTpl('client_secret', '/^.{0,1024}$/', $prefill['client_secret'])
  : new InputTpl('client_secret', '/^.{0,1024}$/');

$widgets = [ $secretInput ];
if ($mode === 'edit') {
    $widgets[] = new TextTpl('<i style="color:#999999">' . _T('(leave blank to keep current)', 'admin') . '</i>');
}

$form->add(
    new TrFormElement(_T("Client secret", "admin"), new multifieldTpl($widgets))
);

$form->add(new TrFormElement(_T("LDAP uid", "admin"),       new InputTpl('ldap_uid', '/^.{0,64}$/')),       ['value' => $prefill['ldap_uid']]);
$form->add(new TrFormElement(_T("LDAP givenName", "admin"), new InputTpl('ldap_givenName', '/^.{0,64}$/')), ['value' => $prefill['ldap_givenName']]);
$form->add(new TrFormElement(_T("LDAP sn", "admin"),        new InputTpl('ldap_sn', '/^.{0,64}$/')),        ['value' => $prefill['ldap_sn']]);
$form->add(new TrFormElement(_T("LDAP mail", "admin"),      new InputTpl('ldap_mail', '/^.{0,64}$/')),      ['value' => $prefill['ldap_mail']]);
$form->add(new TrFormElement(_T("Proxy URL", "admin"),      new InputTpl('proxy_url', '/^.{0,400}$/')),     ['value' => $prefill['proxy_url']]);

// to activate later (let commented for now):
// $form->add(new TrFormElement(_T("Profiles order", "admin"),  new InputTpl('profiles_order', '/^.{0,400}$/')), ['value' => ($prefill['profiles_order'] ?? '')]);
// // Si vous avez un TextareaTpl, remplacez InputTpl par TextareaTpl('acls_json')
// $form->add(new TrFormElement(_T("ACLs (JSON map role->acl)", "admin"), new InputTpl('acls_json', '/^.{0,65535}$/')), [
//     'value' => $prefill['acls_json'] ?? ''
// ]);

$form->add(new HiddenTpl('mode'), ['value' => $mode, 'hide' => true]);
$form->add(new HiddenTpl('id'),   ['value' => (string)$prefill['id'], 'hide' => true]);

$form->pop();
$form->display();
?>

<script>
jQuery(function($){
  const ID = 'client_secret';
  const OPEN_ICON  = 'img/login/open.svg';
  const CLOSE_ICON = 'img/login/close.svg';

  const $inp = $('#'+ID);
  if (!$inp.length) return;

  let $wrap = $('#container_input_'+ID);
  if (!$wrap.length) {
    $inp.wrap('<span class="pw-wrap"></span>');
    $wrap = $inp.parent();
  } else {
    $wrap.addClass('pw-wrap');
  }

  let $btn = $wrap.find('.pw-toggle[data-for="'+ID+'"]');
  if (!$btn.length) {
    $btn = $(`
      <button type="button" class="pw-toggle" data-for="${ID}"
              aria-label="Afficher" aria-pressed="false"
              data-open="${OPEN_ICON}" data-close="${CLOSE_ICON}">
        <img class="pw-icon" alt="">
      </button>
    `).appendTo($wrap);
  }
  if (!$btn.find('img.pw-icon').length) {
    $btn.append('<img class="pw-icon" alt="">');
  }
  const $icon = $btn.find('.pw-icon');

  function applyState(){
    const isEmpty = ($inp.val() === '');
    const hidden  = !isEmpty;
    $inp.attr('type', hidden ? 'password' : 'text');
    $icon.attr('src', hidden ? $btn.data('close') : $btn.data('open'));
    $btn.attr({
      'aria-label': hidden ? 'Afficher le secret' : 'Masquer le secret',
      'aria-pressed': !hidden
    });
  }

  $btn.on('click', function(){
    if ($inp.val() !== '') {
      const isPwd = ($inp.attr('type') === 'password');
      $inp.attr('type', isPwd ? 'text' : 'password');
      const nowHidden = !isPwd;
      $icon.attr('src', nowHidden ? $btn.data('close') : $btn.data('open'));
      $btn.attr({
        'aria-label': nowHidden ? 'Afficher le secret' : 'Masquer le secret',
        'aria-pressed': !nowHidden
      });
    }
    $inp.trigger('focus');
  });

  $inp.on('input', applyState);

  applyState();
});
</script>