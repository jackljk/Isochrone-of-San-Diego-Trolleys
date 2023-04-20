// For address / latlng radio buttons
window.addEventListener("load", function() {
    var latlng_fields = document.getElementById("latlng_fields");
    var address_fields = document.getElementById("address_fields");

    var latlng_radio = document.getElementById("latlng");
    var address_radio = document.getElementById("address");

    latlng_radio.addEventListener("click", function() {
        latlng_fields.style.display = "block";
        address_fields.style.display = "none";
    });

    address_radio.addEventListener("click", function() {
        latlng_fields.style.display = "none";
        address_fields.style.display = "block";
    });
});

// For avg speed using E-bikes
window.addEventListener("load", function() {
    var transportSelection = document.getElementById("transportSelection");
    var avgSpeedDiv = document.getElementById("avgspeed");

    transportSelection.addEventListener("change", function() {
        if (transportSelection.value == "eBike") {
            avgSpeedDiv.style.display = "block";
            console.log("eBike selected");
        } else {
            avgSpeedDiv.style.display = "none";
        }
    });
});

// For the avg speed selector
window.addEventListener("load", function() {
    var selector = document.getElementById("avgSpeedSelector");

    for (var i = 10; i < 21; i++) {
        var option = document.createElement("option");
        option.text = i;
        option.value = i;
        if (i == 20) {
            option.selected = true;
        }
        selector.add(option);
    }
});

// Open APPID and API input popup
window.addEventListener("load", function() {
    var popup = document.getElementById("API-info");
    var popupBtn = document.getElementById("API-info-button-open");
    var closeBtn = document.getElementById("API-info-button-close");

    popupBtn.addEventListener("click", function() {
        popup.style.display = "block";
    });

    closeBtn.addEventListener("click", function() {
        popup.style.display = "none";
    });
});

// To open sidebar on button click
window.addEventListener("load", function() {
    var sidebar = document.querySelector(".sidebar");
    var sidebarBtn = document.getElementById("sidebar-open");

    sidebarBtn.addEventListener("click", function() {
        if (sidebar.style.display == "none") {
            sidebar.style.display = "block";
        } else {
            sidebar.style.display = "none";
        }
    });

});
