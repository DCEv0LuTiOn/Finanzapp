/**
 * 1. TRANSATION EDIT POPUP
 */
function openEditPopup(id, iban, name, zweck, betrag, datum, artId, bemerkung, katId) {
    const modal = document.getElementById('editModal');
    
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-iban-beteiligter').value = (iban !== 'None' && iban !== '') ? iban : '';
    document.getElementById('edit-name-beteiligter').value = (name !== 'None' && name !== '') ? name : '';
    document.getElementById('edit-zweck').value = (zweck !== 'None' && zweck !== '') ? zweck : '';
    document.getElementById('edit-betrag').value = betrag;
    datum = datum.split(".").reverse().join("-")
    document.getElementById('edit-datum').value = datum;
    document.getElementById('edit-bemerkung').value = (bemerkung !== 'None' && bemerkung !== '') ? bemerkung : '';
    
    const artSelect = document.getElementById('edit-buchungsart');
    if (artSelect) artSelect.value = artId;

    const katSelect = document.getElementById('edit-kategorie');
    if (katSelect) katSelect.value = (katId && katId !== 'None') ? katId : 'null';

    modal.style.display = "block";
}

function closePopup() {
    document.getElementById('editModal').style.display = "none";
}

/**
 * 2. KONTEN VERWALTUNG (LISTE & SINGLE EDIT)
 */
function openManageKontenPopup() {
    document.getElementById('manageKontenModal').style.display = "block";
}

function closeManageKonten() {
    document.getElementById('manageKontenModal').style.display = "none";
}

function openKontoEditSingle(iban, name) {
    document.getElementById('single-edit-konto-iban').value = iban;
    document.getElementById('display-konto-iban').value = iban;
    document.getElementById('single-edit-konto-name').value = name;
    document.getElementById('editKontoSingleModal').style.display = "block";
}

function closeKontoEditSingle() {
    document.getElementById('editKontoSingleModal').style.display = "none";
}

/**
 * 3. KATEGORIEN VERWALTUNG (LISTE & SINGLE EDIT)
 */
function openManageKategorienPopup() {
    document.getElementById('manageKategorienModal').style.display = "block";
}

function closeManageKategorien() {
    document.getElementById('manageKategorienModal').style.display = "none";
}

function openKategorieEditSingle(id, bezeichnung) {
    document.getElementById('single-edit-kat-id').value = id;
    document.getElementById('single-edit-kat-bezeichnung').value = bezeichnung;
    document.getElementById('editKategorieSingleModal').style.display = "block";
}

function closeKategorieEditSingle() {
    document.getElementById('editKategorieSingleModal').style.display = "none";
}

/**
 * GLOBALER CLICK-HANDLER (Schließen beim Klick nach draußen)
 */
window.onclick = function(event) {
    // Liste aller Modals
    const modals = {
        'editModal': closePopup,
        'manageKontenModal': closeManageKonten,
        'editKontoSingleModal': closeKontoEditSingle,
        'manageKategorienModal': closeManageKategorien,
        'editKategorieSingleModal': closeKategorieEditSingle
    };

    // Prüfen, ob das geklickte Element eines der Modals ist
    for (let id in modals) {
        if (event.target == document.getElementById(id)) {
            modals[id]();
        }
    }
};