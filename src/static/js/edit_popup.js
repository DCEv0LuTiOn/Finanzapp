function openEditPopup(id, iban, name, zweck, betrag, datum, artId, bemerkung, katId) {
    const modal = document.getElementById('editModal');
    
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-iban-beteiligter').value = (iban !== 'None' && iban !== '') ? iban : '';
    document.getElementById('edit-name-beteiligter').value = (name !== 'None' && name !== '') ? name : '';
    document.getElementById('edit-zweck').value = (zweck !== 'None' && zweck !== '') ? zweck : '';
    document.getElementById('edit-betrag').value = betrag;
    document.getElementById('edit-datum').value = datum;
    document.getElementById('edit-bemerkung').value = (bemerkung !== 'None' && bemerkung !== '') ? bemerkung : '';
    
    // Buchungsart Dropdown setzen
    const artSelect = document.getElementById('edit-buchungsart');
    if (artSelect) {
        artSelect.value = artId;
    }

    // Kategorie Dropdown setzen
    const katSelect = document.getElementById('edit-kategorie');
    if (katSelect) {
        katSelect.value = (katId && katId !== 'None') ? katId : 'null';
    }

    modal.style.display = "block";
}

function closePopup() {
    document.getElementById('editModal').style.display = "none";
}

window.onclick = function(event) {
    const modal = document.getElementById('editModal');
    if (event.target == modal) {
        closePopup();
    }
};