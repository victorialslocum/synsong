window.onload = function () {
  let refButtonDiv = document.getElementById("genreButtons");
  let publicButton = document.getElementById("publicButton");
  let visDiv = document.getElementById("visibility");
  let privateButton = document.getElementById("privateButton");
  let inputForm = document.getElementById("inputForm");
  let hiddenElement = document.getElementById("hidden");
  let hiddenElementVis = document.getElementById("hiddenvis");
  let submitButton = document.getElementById("submitButton");
  let genreList = [];

  for (var i = 0; i < refButtonDiv.children.length; i++) {
    let button = refButtonDiv.children[i].children[0];

    button.onclick = function () {
      let selectedCount = 0;
      for (var i = 0; i < refButtonDiv.children.length; i++) {
        let button = refButtonDiv.children[i].children[0];
        if (button.classList.contains("is-focused")) {
          selectedCount++;
        }
      }
      if (this.classList.contains("is-focused")) {
        this.classList.remove("is-focused");
      } else {
        if (selectedCount >= 3) {
          alert("you can only select 3 genres");
        } else {
          this.classList.add("is-focused");
        }
      }
    };
  }

  publicButton.onclick = function () {
    if (publicButton.classList.contains("is-focused")) {
      privateButton.classList.add("is-focused");
      publicButton.classList.remove("is-focused");
    } else {
      publicButton.classList.add("is-focused");
      privateButton.classList.remove("is-focused");
    }
  };

  privateButton.onclick = function () {
    if (privateButton.classList.contains("is-focused")) {
      publicButton.classList.add("is-focused");
      privateButton.classList.remove("is-focused");
    } else {
      privateButton.classList.add("is-focused");
      publicButton.classList.remove("is-focused");
    }
  };

  submitButton.onclick = function () {
    console.log("success");
    for (var i = 0; i < refButtonDiv.children.length; i++) {
      let button = refButtonDiv.children[i].children[0];
      if (button.classList.contains("is-focused")) {
        genreList.push(button.name);
      }
    }

    if (privateButton.classList.contains("is-focused")) {
      hiddenElementVis.setAttribute("value", "False");
    } else {
      hiddenElementVis.setAttribute("value", "True");
    }
    hiddenElement.setAttribute("value", genreList);

    inputForm.submit();
  };
};
