setTimeout(function(){
    /*
    Event Binding Beg
    */
    function Save(input) {
        return new Promise((resolve, reject)=>{
            let data = {};
            for(let inp of $(`input[path="${$(input).attr("path")}"]`)) {
                switch($(inp).attr("type")) {
                    case "checkbox":
                        data[$(inp).attr("name")] = $(inp).is(":checked");
                        break;
                    default:
                        data[$(inp).attr("name")] = $(inp).val();
                        break;
                }
            }
            return resolve(data);
        }).then((data)=>{
            return $.post(`/app/config/${$(input).attr("path")}`, JSON.stringify(data));
        });
    }
    function SetRegion(data) {
        let w = window.screen.width;
        let h = window.screen.height;
        let o = Math.round(h/6);
        let p = Object.entries({
            "region-l": w - o*3,
            "region-t": h - o,
            "region-r": w,
            "region-b": h,
        }).map(([key, value])=>{
            let saved = parseInt(data[key]);
            let coord = (isNaN(saved) || saved < 0) ? value : saved;
            $(`input[name="${key}"]`).val(coord);
            return Promise.resolve(coord);
        });

        return Promise.all(p).then(()=>{
            return Save($("input[path='settings.json']"));
        });
    }
    function Bind(parent) {
        $(parent)
            .find(".slider-input")
                .on("input", function(){
                    let slider = $(this).siblings(".slider");
                    let min = parseFloat(slider.attr("min"));
                    let max = parseFloat(slider.attr("max"));
                    let txt = $(this).val().replace(/[^0-9\.]/g, "");
                    let val = parseFloat(txt);
                    if(!isNaN(val)) {
                        let value = Math.max(min, Math.min(val, max));
                        $(this).val(txt);
                        slider.val(value);
                        Save(this);
                    }
                    else {
                        $(this).val(parseFloat(slider.val()).toFixed(parseInt($(this).attr("decimals"))||0));
                    }
                })
                .on("focusout", function(){
                    let slider = $(this).siblings(".slider");
                    let min = parseFloat(slider.attr("min"));
                    let max = parseFloat(slider.attr("max"));
                    let val = parseFloat($(this).val());
                    let value = Math.max(min, Math.min(val, max));
                    $(this).val(value.toFixed(parseInt($(this).attr("decimals"))||0));
                    slider.val(value);
                    Save(this);
                });
        $(parent)
            .find(".slider")
                .on("input", function(){
                    let input = $(this).siblings(".slider-input");
                    let value = parseFloat($(this).val());
                    input.val(value.toFixed(parseInt(input.attr("decimals"))||0));
                })
                .on("focusout", function(){
                    Save(this);
                });
        $(parent)
            .find(".switch")
                .on("change", function(){
                    Save(this);
                });
        $(parent)
            .find(".color")
                .on("change", function(){
                    Save(this);
                });
        $(parent)
            .find(".keybind")
                .on("mousedown", function(e){
                    if(!$(this).is(":focus")) return;
                    else if(e.button == 0) return;
                    else if(e.button == 2) $(this).val(MBUTTON2KEY[3]);
                    else if(e.button in MBUTTON2KEY) $(this).val(MBUTTON2KEY[e.button]);
                    $(this).blur();
                    e.preventDefault();
                    Save(this);
                })
                .on("keydown", function(e){
                    if(!$(this).is(":focus")) return;
                    if(e.keyCode in KEYCODE2KEY) $(this).val(KEYCODE2KEY[e.keyCode]);
                    $(this).blur();
                    e.preventDefault();
                    Save(this);
                });
        $(parent)
            .find(".region-button")
                .on("mousedown", function(e){
                    // window.Notify("error", window.GetLangText("app-feature-developing"));
                    switch(e.which) {
                        case 1:
                            $.post("/app/controls/app-control-region");
                            break;
                        default:
                            SetRegion({});
                            break;
                    }
                });
        return $(parent);
    }
    /*
    Event Binding End
    */


    /*
    Load Data Beg
    */
    Promise.all([
        Bind($("#page")),
        $.get("/app/config/settings.json", {})
            .then((data)=>{
                for(key in data) {
                    let inp = $(`input[name="${key}"]`);
                    switch($(inp).attr("type")) {
                        case "checkbox":
                            $(inp).prop("checked", data[key]);
                            break;
                        default:
                            $(inp).val(data[key]);
                            break;
                    }
                }
                return SetRegion(data);
            }),
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
                let sortedAmmoOrder = Object.keys(weaponsGrouped)
                                        .sort((a, b)=>{
                                            let va = a.split("").reduce((p,c)=>(p+c.charCodeAt(0)), 0)/a.length
                                            let vb = b.split("").reduce((p,c)=>(p+c.charCodeAt(0)), 0)/b.length
                                            return va - vb;
                                        });
                let weaponSettingsHtml = (sortedAmmoOrder.map(group=>{
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
                                        <h5 class="name lang" lang="page-settings-mult">${window.GetLangText("page-settings-mult")}</h5>
                                        <form action="javascript:void(0);">
                                            <input class="slider" type="range" min="0" max="2" step="0.1" value="${weapon.multiplier}" path="weapons/${weapon.name}.json" name="multiplier">
                                            <input class="slider-input" type="text" value="${weapon.multiplier}" decimals="1" path="weapons/${weapon.name}.json" name="multiplier">
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
            }),
    ]).then(()=>{
        $(".adjustment").on("mouseenter", function(){
            if(!$(this).attr("tooltip")) return;
            let tip = window.Tooltip(window.GetLangText($(this).attr("tooltip")));
            $(tip).on("mouseleave", function(){ $(this).remove() });
            $(this).on("remove mouseleave", function(){ $(tip).remove() });
        });
    });
    /*
    Load Data End
    */
}, 100);