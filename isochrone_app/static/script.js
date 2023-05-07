// For address / latlng radio buttons
window.addEventListener("load", function () {
  var latlng_fields = document.getElementById("latlng_fields");
  var address_fields = document.getElementById("address_fields");
  var trolley_fields = document.getElementById("trolley_fields");
  var submit_button = document.getElementById("join-btn");

  var latlng_radio = document.getElementById("option-1");
  var address_radio = document.getElementById("option-2");
  var trolley_radio = document.getElementById("option-3");

  latlng_radio.addEventListener("click", function () {
    latlng_fields.style.display = "block";
    address_fields.style.display = "none";
    trolley_fields.style.display = "none";
    submit_button.style.display = "block";
  });

  address_radio.addEventListener("click", function () {
    latlng_fields.style.display = "none";
    address_fields.style.display = "block";
    trolley_fields.style.display = "none";
    submit_button.style.display = "block";
  });

  trolley_radio.addEventListener("click", function () {
    latlng_fields.style.display = "none";
    address_fields.style.display = "none";
    trolley_fields.style.display = "flex";
    submit_button.style.display = "none";
  });
});

// For avg speed using E-bikes
window.addEventListener("load", function () {
  var transportSelection = document.getElementById("checkbox-ebike");
  var avgSpeedDiv = document.getElementById("avgspeed");

  // only show avg speed if ebike is selected
  transportSelection.addEventListener("click", function () {
    if (transportSelection.checked) {
      avgSpeedDiv.style.display = "block";
    } else {
      avgSpeedDiv.style.display = "none";
    }
  }
  );
});

// For the avg speed selector
window.addEventListener("load", function () {
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
window.addEventListener("load", function () {
  var popup = document.getElementById("API-info");
  var popupBtn = document.getElementById("API-info-button-open");
  var closeBtn = document.getElementById("API-info-button-close");

  popupBtn.addEventListener("click", function () {
    popup.style.display = "block";
  });

  closeBtn.addEventListener("click", function () {
    popup.style.display = "none";
  });
});

// For the sidebar
window.addEventListener("load", function () {
  button = document.getElementById("sidebar-button");
  button.addEventListener("click", function () {
    const sidebar = document.querySelector('.sidebar');
    const sidebarButton = document.getElementById("sidebar-button");
    const computedStyles = getComputedStyle(sidebar);
    console.log(computedStyles.width);
    if (computedStyles.width != "0px") {
      sidebar.style.width = "0";
      sidebar.style.left = "-50px";

      sidebarButton.style.left = "50px";
      sidebarButton.style.backgroundColor = "rgba(231, 235, 235, 0.8)";
    } else if (computedStyles.width == "0px") {
      sidebar.style.width = "400px";
      sidebar.style.left = "0px";

      sidebarButton.style.left = "375px";
      sidebarButton.style.backgroundColor = "transparent";
    }
  });

  var dropdown = document.getElementsByClassName("dropdown-button");
  var i;

  for (i = 0; i < dropdown.length; i++) {
    dropdown[i].addEventListener("click", function () {
      this.classList.toggle("active");
      console.log("clicked");
      var dropdownContent = this.nextElementSibling;
      if (dropdownContent.style.display === "block") {
        dropdownContent.style.display = "none";
      } else {
        dropdownContent.style.display = "block";
      }
    });
  }


});


// For forms
var alertRedInput = "#8C1010";
var defaultInput = "rgba(10, 180, 180, 1)";

function userNameValidation(usernameInput) {
    var username = document.getElementById("username");
    var issueArr = [];
    if (/[-!@#$%^&*()_+|~=`{}\[\]:";'<>?,.\/]/.test(usernameInput)) {
        issueArr.push("No special characters!");
    }
    if (issueArr.length > 0) {
        username.setCustomValidity(issueArr);
        username.style.borderColor = alertRedInput;
    } else {
        username.setCustomValidity("");
        username.style.borderColor = defaultInput;
    }
}

function passwordValidation(passwordInput) {
    var password = document.getElementById("password");
    var issueArr = [];
    if (!/^.{7,15}$/.test(passwordInput)) {
        issueArr.push("Password must be between 7-15 characters.");
    }
    if (!/\d/.test(passwordInput)) {
        issueArr.push("Must contain at least one number.");
    }
    if (!/[a-z]/.test(passwordInput)) {
        issueArr.push("Must contain a lowercase letter.");
    }
    if (!/[A-Z]/.test(passwordInput)) {
        issueArr.push("Must contain an uppercase letter.");
    }
    if (issueArr.length > 0) {
        password.setCustomValidity(issueArr.join("\n"));
        password.style.borderColor = alertRedInput;
    } else {
        password.setCustomValidity("");
        password.style.borderColor = defaultInput;
    }
}