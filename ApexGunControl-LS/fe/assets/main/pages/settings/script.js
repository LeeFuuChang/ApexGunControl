(function(){
    /*
    Event Binding Beg
    */
    function Save(input) {
        return new Promise((resolve, reject)=>{
            let data = {};
            for(let inp of $(`input[path="${$(input).attr("path")}"]`)) {
                data[$(inp).attr("name")] = $(inp).val();
            }
            return resolve(data);
        }).then((data)=>{
            return $.post(`/app/config/${$(input).attr("path")}.json`, JSON.stringify(data))
        });
    };
    function Bind(parent) {
        $(parent)
            .find(".slider-input")
                .on("input", function(){
                    let slider = $(this).siblings(".slider");
                    let min = parseFloat(slider.attr("min"));
                    let max = parseFloat(slider.attr("max"));
                    let val = parseFloat($(this).val());
                    let value = Math.max(min, Math.min(val, max));
                    slider.val(value);
                    Save(this);
                })
                .on("focusout", function(){
                    let slider = $(this).siblings(".slider");
                    let min = parseFloat(slider.attr("min"));
                    let max = parseFloat(slider.attr("max"));
                    let val = parseFloat($(this).val());
                    let value = Math.max(min, Math.min(val, max));
                    $(this).val(value.toFixed(1));
                    slider.val(value);
                    Save(this);
                });
        $(parent)
            .find(".slider")
                .on("input", function(){
                    let input = $(this).siblings(".slider-input");
                    let value = parseFloat($(this).val());
                    input.val(value.toFixed(1));
                })
                .on("focusout", function(){
                    Save(this);
                });
        $(parent)
            .find(".region-button")
                .on("click", function(){
                    $.post("/app/controls/app-control-region");
                });
        return $(parent);
    }
    /*
    Event Binding End
    */


    /*
    Load Data Beg
    */
    Bind($("#page"));
    $.get("/app/config/settings.json", {})
        .then((data)=>{
            let w = window.screen.width;
            let h = window.screen.height;
            let b = Math.round(h/6);
            $("input[name='region-l']").val(w-b*3)
            $("input[name='region-t']").val(h-b)
            $("input[name='region-r']").val(w)
            $("input[name='region-b']").val(h)
            for(key in data) {
                $(`input[name="${key}"]`).val(data[key]);
            }
            return Save($("input[path='settings']"));
        });
    $.get("/app/config/weapons", {})
        .then((list)=>{
            return Promise.all(list.map((file)=>{
                return $.get(`/app/config/weapons/${file}`, {})
            }));
        })
        .then((weaponsData)=>{
            let weaponsGrouped = {};
            for(weapon of weaponsData) {
                let key = weapon.supply?"Supply":weapon.ammo;
                if(!weaponsGrouped[key]) {
                    weaponsGrouped[key] = [ weapon ];
                }
                else {
                    weaponsGrouped[key].push(weapon);
                }
            }
            return Promise.resolve(weaponsGrouped);
        })
        .then((weaponsGrouped)=>{
            let weaponSettingsHtml = (Object.keys(weaponsGrouped).map(group=>{
                weaponsGrouped[group].sort(function(a, b){
                    return a.name.localeCompare(b.name);
                });
                let ammoWeaponsOptions = weaponsGrouped[group].reduce((html, weapon)=>{
                    return html + `
                        <section class="option">
                            <div class="image">
                                <img class="weapon" src="${weapon.image}" alt="">
                                <h4 class="name">${weapon.name}</h4>
                                <img class="bullet" src="/apex/assets/bullets/${weapon.supply?"Supply":""}${weapon.ammo}.png" alt="">
                            </div>
                            <div class="group">
                                <div class="adjustment">
                                    <h5 class="name lang" lang="page-settings-mult">GC Multiplier</h5>
                                    <form action="javascript:void(0);">
                                        <input class="slider" type="range" min="0" max="2" step="0.1" value="${weapon.multiplier}" path="weapons/${weapon.name}" name="multiplier">
                                        <input class="slider-input" type="text" value="${weapon.multiplier}" path="weapons/${weapon.name}" name="multiplier">
                                    </form>
                                </div>
                            </div>
                        </section>
                        `;
                }, "");
                return `
                    <section class="category">
                        <h3 class="title">${group}</h3>
                        ${ammoWeaponsOptions}
                    </section>
                    `;
            })).join("");
            return Promise.resolve(weaponSettingsHtml);
        })
        .then((weaponSettingsHtml)=>{
            Bind($(weaponSettingsHtml)).appendTo($("#page[name='settings'] .container"));
        });
    /*
    Load Data End
    */
})();

