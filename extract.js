(function() {
  var data = {};
  data.title = document.querySelector('#product_title') ? document.querySelector('#product_title').value : '';

  var gallerySection = document.querySelector('#gallery');
  var hiddenInputs = gallerySection ? gallerySection.querySelectorAll('input[type=hidden]') : [];
  data.coverImage = '';
  data.galleryImages = [];
  for(var i=0; i<hiddenInputs.length; i++) {
    var val = hiddenInputs[i].value;
    var name = hiddenInputs[i].name;
    if(val && val.includes('superhivemarket.com')) {
      if(name === 'product[image]') {
        data.coverImage = val.split('|').pop();
      } else {
        data.galleryImages.push(val.split('|').pop());
      }
    }
  }

  var descSection = document.querySelector('#description');
  var descTextarea = descSection ? descSection.querySelector('textarea') : null;
  data.description = descTextarea ? btoa(unescape(encodeURIComponent(descTextarea.value))) : '';

  var docsSection = document.querySelector('#documentation');
  var docsTextarea = docsSection ? docsSection.querySelector('textarea') : null;
  data.documentation = docsTextarea ? btoa(unescape(encodeURIComponent(docsTextarea.value))) : '';

  var filesSection = document.querySelector('#files');
  data.files = [];
  if(filesSection) {
    var fileLinks = filesSection.querySelectorAll('a[href*=cloudflarestorage]');
    var fileNames = [];
    var allText = filesSection.innerText;
    var lines = allText.split('\n');
    for(var i=0; i<lines.length; i++) {
      var line = lines[i].trim();
      if(line.match(/\.(zip|blend|py|rar|7z|pdf|txt)$/i)) {
        fileNames.push(line);
      }
    }
    for(var i=0; i<fileLinks.length; i++) {
      data.files.push({
        url: fileLinks[i].href,
        name: (i < fileNames.length) ? fileNames[i] : ('file_' + i + '.zip')
      });
    }
  }

  var descDiv = document.createElement('div');
  if(descTextarea) descDiv.innerHTML = descTextarea.value;
  var descImgs = descDiv.querySelectorAll('img');
  data.descriptionImages = [];
  for(var i=0; i<descImgs.length; i++) {
    var src = descImgs[i].getAttribute('src');
    if(src) data.descriptionImages.push(src);
  }

  data.price = '';
  var priceEl = document.querySelector('.price-box span:last-child');
  if(priceEl) data.price = priceEl.textContent.trim();

  return JSON.stringify(data);
})()
