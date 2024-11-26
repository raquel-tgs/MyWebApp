// Collapsible Menu Logic

var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    } 
  });
}

// Modal Logic

function updater() {
  $.get('/data', function(data) {
    var splitData = data.split('#');
    $('#time').html(splitData[0]);  // update page with new data

    if (splitData[1] === "Enabled") {
      $('#op-modal-btn-close').removeClass("hide-block")
      $('#op-modal-btn-cancel').removeClass("show-block")

      $('#op-modal-btn-close').addClass("show-block")
      $('#op-modal-btn-cancel').addClass("hide-block")

      $('#modal-title').addClass('display-none')
      $('#modal-title').removeClass('flex')
      $('#modal-title-complete').addClass('flex')
      $('#modal-title-complete').removeClass('display-none')
    } else {
      $('#op-modal-btn-close').removeClass("show-block")
      $('#op-modal-btn-cancel').removeClass("hide-block")

      $('#op-modal-btn-close').addClass("hide-block")
      $('#op-modal-btn-cancel').addClass("show-block")

      $('#modal-title').removeClass('display-none')
      $('#modal-title').addClass('flex')
      $('#modal-title-complete').addClass('display-none')
      $('#modal-title-complete').removeClass('flex')
    }
  });
};

// This needs to go, but some logic is needed...
function updater_bar() {
  $.get('/databar', function(data) {
    $('#myprogressBar').css('width', data);;  // update page with new data
  });
};

function updater_statuslog() {
  $.get('/data_statuslog', function(data) {
    $('#statuslog').text(data);  // update page with new data
  });
};

setInterval(updater, 1000);  // run `updater()` every 1000ms (1s)
setInterval(updater_bar, 2000);  // run `updater_bar()` every 2000ms (2s)
setInterval(updater_statuslog, 1000);  // run `updater_statuslog()` every 1000ms (1s)
