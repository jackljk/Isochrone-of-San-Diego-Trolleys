
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