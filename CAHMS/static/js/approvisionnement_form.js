document.addEventListener('DOMContentLoaded', function () {
    const formsetArea = document.getElementById('formset-area');
    const addRowBtn = document.getElementById('add-row-btn');
    const emptyFormDiv = document.getElementById('empty-form');
    const totalForms = document.querySelector('input[name$="-TOTAL_FORMS"]');

    // Vérification que tous les éléments nécessaires existent
    if (!formsetArea || !addRowBtn || !emptyFormDiv || !totalForms) {
        console.error('Éléments requis manquants pour le formset dynamique');
        return;
    }

    function updateProduitOptions() {
        const selects = formsetArea.querySelectorAll('select[name$="produit"]');
        const selectedValues = Array.from(selects).map(s => s.value).filter(v => v);
        selects.forEach(select => {
            const currentValue = select.value;
            Array.from(select.options).forEach(option => {
                option.disabled = option.value && option.value !== currentValue && selectedValues.includes(option.value);
            });
        });
    }

    addRowBtn.addEventListener('click', function () {
        const formCount = parseInt(totalForms.value);
        // On clone le contenu HTML du empty-form (pas juste le premier enfant)
        const newRow = emptyFormDiv.innerHTML.replace(/__prefix__/g, formCount);
        // On crée un élément temporaire pour parser le HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = newRow;
        // On ajoute le premier enfant (la row) dans la zone formset
        formsetArea.appendChild(tempDiv.firstElementChild);
        totalForms.value = formCount + 1;
        updateProduitOptions();
    });

    formsetArea.addEventListener('click', function (e) {
        if (e.target.closest('.btn-remove-row')) {
            const row = e.target.closest('.formset-row');
            const deleteInput = row.querySelector('input[type="checkbox"][name$="DELETE"]');
            if (deleteInput) {
                deleteInput.checked = true;
                row.style.display = 'none';
            } else {
                row.remove();
                totalForms.value = formsetArea.querySelectorAll('.formset-row').length;
            }
            updateProduitOptions();
        }
    });

    formsetArea.addEventListener('change', function (e) {
        if (e.target && e.target.matches('select[name$="produit"]')) {
            updateProduitOptions();
        }
    });

    function getMontantDemandeForSelectedSortie() {
        const sortieSelect = document.querySelector('select[name$="sortie_fond"]');
        if (!sortieSelect) return 0;
        const selectedOption = sortieSelect.options[sortieSelect.selectedIndex];
        // On va chercher le montant dans le label (extraction simple)
        const match = selectedOption.textContent.match(/([0-9]+(?:[.,][0-9]+)?) FC/);
        if (match) {
            return parseFloat(match[1].replace(',', '.'));
        }
        return 0;
    }

    function updateObservationWithTotal() {
        const observation = document.querySelector('textarea[name$="observation"]');
        const sortieMontant = getMontantDemandeForSelectedSortie();
        let total = 0;
        document.querySelectorAll('.formset-row').forEach(row => {
            const select = row.querySelector('select[name$="produit"]');
            const quantiteInput = row.querySelector('input[name$="quantite"]');
            if (select && quantiteInput && select.value) {
                const prix = window.PRODUIT_PRIX[select.value] || 0;
                const quantite = parseInt(quantiteInput.value) || 0;
                total += prix * quantite;
            }
        });
        let remarque = '';
        if (total > sortieMontant) {
            remarque = `Le total des produits (${total.toFixed(2)} FC) est SUPÉRIEUR au montant de la demande de fonds (${sortieMontant.toFixed(2)} FC).`;
        } else if (total < sortieMontant) {
            remarque = `Le total des produits (${total.toFixed(2)} FC) est INFÉRIEUR au montant de la demande de fonds (${sortieMontant.toFixed(2)} FC).`;
        } else if (total === sortieMontant && total !== 0) {
            remarque = `Le total des produits est ÉGAL au montant de la demande de fonds (${total.toFixed(2)} FC).`;
        }
        if (observation) {
            observation.value = remarque;
        }
    }

    // Sur chaque changement de produit, quantité ou sortie_fond
    ['change', 'input'].forEach(evt => {
        document.addEventListener(evt, function(e) {
            if (
                e.target.matches('select[name$="produit"]') ||
                e.target.matches('input[name$="quantite"]') ||
                e.target.matches('select[name$="sortie_fond"]')
            ) {
                updateObservationWithTotal();
            }
        });
    });

    updateProduitOptions();
}); 