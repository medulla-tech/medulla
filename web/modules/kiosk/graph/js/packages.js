/**
 * (c) 2018 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

function kioskProfilePackages() {
    var uuids = [];
    jQuery("#profile-packages li").each(function(){
        uuids.push(jQuery(this).attr('data-uuid'));
    });
    return uuids;
}

(function() {
    var KEY_ENTER = 13, KEY_ESCAPE = 27, KEY_SPACE = 32, KEY_M = 77;
    var targets = document.querySelectorAll('[data-draggable="target"]');
    var items = document.querySelectorAll('[data-draggable="item"]');
    var selections = {items: [], owner: null, droptarget: null};
    var related = null;
    var i;

    for(i = 0; i < targets.length; i++)
        targets[i].setAttribute('aria-dropeffect', 'none');

    for(i = 0; i < items.length; i++) {
        items[i].setAttribute('draggable', 'true');
        items[i].setAttribute('aria-grabbed', 'false');
        items[i].setAttribute('tabindex', '0');
    }

    // A selection stays inside one list, the owner.
    function addSelection(item) {
        if(!selections.owner)
            selections.owner = item.parentNode;
        else if(selections.owner != item.parentNode)
            return;
        item.setAttribute('aria-grabbed', 'true');
        selections.items.push(item);
    }

    function removeSelection(item) {
        var index = selections.items.indexOf(item);
        item.setAttribute('aria-grabbed', 'false');
        if(index !== -1)
            selections.items.splice(index, 1);
        if(!selections.items.length)
            selections.owner = null;
    }

    function clearSelections() {
        if(!selections.items.length)
            return;
        selections.owner = null;
        for(var i = 0; i < selections.items.length; i++)
            selections.items[i].setAttribute('aria-grabbed', 'false');
        selections.items = [];
    }

    function hasModifier(e) {
        return (e.ctrlKey || e.metaKey || e.shiftKey);
    }

    // Opens the other lists to the drop and takes their items out of the tab order.
    function addDropeffects() {
        var i;
        for(i = 0; i < targets.length; i++) {
            if(targets[i] != selections.owner && targets[i].getAttribute('aria-dropeffect') == 'none') {
                targets[i].setAttribute('aria-dropeffect', 'move');
                targets[i].setAttribute('tabindex', '0');
            }
        }
        for(i = 0; i < items.length; i++) {
            if(items[i].parentNode != selections.owner && items[i].getAttribute('aria-grabbed')) {
                items[i].removeAttribute('aria-grabbed');
                items[i].removeAttribute('tabindex');
            }
        }
    }

    function clearDropeffects() {
        var i;
        if(!selections.items.length)
            return;
        for(i = 0; i < targets.length; i++) {
            if(targets[i].getAttribute('aria-dropeffect') != 'none') {
                targets[i].setAttribute('aria-dropeffect', 'none');
                targets[i].removeAttribute('tabindex');
            }
        }
        for(i = 0; i < items.length; i++) {
            if(!items[i].getAttribute('aria-grabbed')) {
                items[i].setAttribute('aria-grabbed', 'false');
                items[i].setAttribute('tabindex', '0');
            } else if(items[i].getAttribute('aria-grabbed') == 'true') {
                items[i].setAttribute('tabindex', '0');
            }
        }
    }

    function getContainer(element) {
        do {
            if(element.nodeType == 1 && element.getAttribute('aria-dropeffect'))
                return element;
        } while(element = element.parentNode);
        return null;
    }

    function moveSelectionTo(target) {
        for(var i = 0; i < selections.items.length; i++)
            target.appendChild(selections.items[i]);
    }

    document.addEventListener('mousedown', function(e) {
        clearDropeffects();
        if(e.target.getAttribute('draggable')) {
            if(!hasModifier(e) && e.target.getAttribute('aria-grabbed') == 'false') {
                clearSelections();
                addSelection(e.target);
            }
        } else if(!hasModifier(e)) {
            clearSelections();
        }
    }, false);

    document.addEventListener('mouseup', function(e) {
        if(e.target.getAttribute('draggable') && hasModifier(e)) {
            if(e.target.getAttribute('aria-grabbed') == 'true')
                removeSelection(e.target);
            else
                addSelection(e.target);
        }
    }, false);

    document.addEventListener('dragstart', function(e) {
        if(selections.owner != e.target.parentNode) {
            e.preventDefault();
            return;
        }
        if(hasModifier(e) && e.target.getAttribute('aria-grabbed') == 'false')
            addSelection(e.target);

        // Firefox does not start a drag without transfer data.
        e.dataTransfer.setData('text', '');
        addDropeffects();
    }, false);

    document.addEventListener('keydown', function(e) {
        if(e.target.getAttribute('aria-grabbed')) {
            if(e.keyCode == KEY_SPACE) {
                if(hasModifier(e)) {
                    if(e.target.getAttribute('aria-grabbed') == 'true') {
                        if(selections.items.length == 1)
                            clearDropeffects();
                        removeSelection(e.target);
                        if(selections.items.length)
                            addDropeffects();
                    } else {
                        addSelection(e.target);
                        addDropeffects();
                    }
                } else if(e.target.getAttribute('aria-grabbed') == 'false') {
                    clearDropeffects();
                    clearSelections();
                    addSelection(e.target);
                    addDropeffects();
                } else {
                    addDropeffects();
                }
                e.preventDefault();
            }

            // Modifier + M ends the selection and moves the focus to the next list.
            if(e.keyCode == KEY_M && hasModifier(e)) {
                if(selections.items.length) {
                    addDropeffects();
                    var index = Array.prototype.indexOf.call(targets, selections.owner);
                    targets[(index + 1) % targets.length].focus();
                }
                e.preventDefault();
            }
        }

        if(e.keyCode == KEY_ESCAPE && selections.items.length) {
            clearDropeffects();
            selections.items[selections.items.length - 1].focus();
            clearSelections();
        }

        if(e.target.getAttribute('aria-dropeffect')
            && (e.keyCode == KEY_ENTER || (e.keyCode == KEY_M && hasModifier(e)))) {
            moveSelectionTo(e.target);
            clearDropeffects();
            selections.items[selections.items.length - 1].focus();
            clearSelections();
            e.preventDefault();
        }
    }, false);

    // dragleave carries no relatedTarget, dragenter keeps it.
    document.addEventListener('dragenter', function(e) {
        related = e.target;
    }, false);

    document.addEventListener('dragleave', function() {
        var droptarget = getContainer(related);
        if(droptarget == selections.owner)
            droptarget = null;

        if(droptarget != selections.droptarget) {
            if(selections.droptarget)
                selections.droptarget.classList.remove('dragover');
            if(droptarget)
                droptarget.classList.add('dragover');
            selections.droptarget = droptarget;
        }
    }, false);

    document.addEventListener('dragover', function(e) {
        if(selections.items.length)
            e.preventDefault();
    }, false);

    document.addEventListener('dragend', function(e) {
        if(selections.droptarget) {
            moveSelectionTo(selections.droptarget);
            e.preventDefault();
        }

        if(selections.items.length) {
            clearDropeffects();
            if(selections.droptarget) {
                clearSelections();
                selections.droptarget.classList.remove('dragover');
                selections.droptarget = null;
            }
        }
    }, false);
})();
