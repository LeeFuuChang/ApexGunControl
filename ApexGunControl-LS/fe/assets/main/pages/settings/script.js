(function(){
    /*
    Dynamic Weapon Settings Beg
    */
    let sortedByAmmo = {};
    for(weapon of window.weaponData) {
        if(!sortedByAmmo[weapon.ammo]) {
            sortedByAmmo[weapon.ammo] = [ weapon ];
        }
        else {
            sortedByAmmo[weapon.ammo].push(weapon);
        }
    }

    let weaponSettingsHtml = (Object.keys(sortedByAmmo).map(ammo=>{
        sortedByAmmo[ammo].sort(function(a, b){
            return a.name.localeCompare(b.name);
        });
        let ammoWeaponsOptions = sortedByAmmo[ammo].reduce((html, weapon)=>{
            return html + `
                <section class="option">
                    <div class="image">
                        <img class="weapon" src="${weapon.image}" alt="">
                        <h4 class="name">${weapon.name}</h4>
                        <img class="bullet" src="assets/media/bullets/${weapon.ammo}.png" alt="">
                    </div>
                    <div class="group">
                        <div class="adjustment">
                            <h5 class="name lang" lang="page-settings-mult">GC Multiplier</h5>
                            <form>
                                <input class="slider" type="range" min="0" max="2" step="0.1" value="${weapon.multiplier}">
                                <input class="slider-input" type="text" value="${weapon.multiplier.toFixed(1)}">
                            </form>
                        </div>
                    </div>
                </section>
                `;
        }, "");
        return `
            <section class="category">
                <h3 class="title">${ammo}</h3>
                ${ammoWeaponsOptions}
            </section>
            `;
    })).join("");

    $(weaponSettingsHtml).appendTo($("#page[name='settings'] .container"));
    /*
    Dynamic Weapon Settings End
    */


    /*
    Event Binding Beg
    */
    $(".slider-input")
        .on("input", function(){
            let slider = $(this).siblings(".slider");
            let min = parseFloat(slider.attr("min"));
            let max = parseFloat(slider.attr("max"));
            let val = parseFloat($(this).val());
            let value = Math.max(min, Math.min(val, max));
            slider.val(value);
        })
        .on("focusout", function(){
            let slider = $(this).siblings(".slider");
            let min = parseFloat(slider.attr("min"));
            let max = parseFloat(slider.attr("max"));
            let val = parseFloat($(this).val());
            let value = Math.max(min, Math.min(val, max));
            $(this).val(value.toFixed(1));
            slider.val(value);
        });
    $(".slider")
        .on("input", function(){
            let input = $(this).siblings(".slider-input");
            let value = parseFloat($(this).val());
            input.val(value.toFixed(1));
        });
})();

