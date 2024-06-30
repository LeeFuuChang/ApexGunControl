(function(){
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
                            <h5 class="name">Need Control</h5>
                            <div class="input" type="switch">
                                <form class="part">
                                    <button data-value="1" class="${weapon.assisting?'active':''}">On</button>
                                    <button data-value="0" class="${weapon.assisting?'':'active'}">Off</button>
                                </form>
                            </div>
                        </div>
                        <div class="adjustment">
                            <h5 class="name">GC Multiplier</h5>
                            <div class="input" type="range">
                                <form class="part">
                                    <input type="range" min="0" max="2" step="0.05" value="${weapon.multiplier}">
                                </form>
                                <form class="part">
                                    <input type="text" value="${weapon.multiplier.toFixed(2)}">
                                </form>
                            </div>
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
})();

