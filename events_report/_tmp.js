(function() {
  var rows = document.querySelectorAll('table tbody tr');
  var events = [];
  for(var i=0; i<rows.length; i++) {
    var cells = rows[i].querySelectorAll('td');
    if(cells.length >= 3) {
      var link = rows[i].querySelector('a[href*="/events/"]');
      var eventId = '';
      if(link) {
        var m = link.href.match(/events\/(\d+)/);
        if(m) eventId = m[1];
      }
      events.push({
        created: cells[0] ? cells[0].textContent.trim() : '',
        event: cells[1] ? cells[1].textContent.trim() : '',
        productId: cells[2] ? cells[2].textContent.trim() : '',
        eventId: eventId
      });
    }
  }
  // Also get summary stats
  var statsText = document.body.innerText;
  var stats = {};
  var viewsMatch = statsText.match(/(\d+)\s*\n\s*Product Views/);
  if(viewsMatch) stats.productViews = viewsMatch[1];
  var cartMatch = statsText.match(/(\d+)\s*\n[\d.]+%\s*\n\s*Added to Cart/);
  if(cartMatch) stats.addedToCart = cartMatch[1];
  var checkoutMatch = statsText.match(/(\d+)\s*\n[\d.]+%\s*\n\s*Reached Checkout/);
  if(checkoutMatch) stats.reachedCheckout = checkoutMatch[1];
  var purchasedMatch = statsText.match(/(\d+)\s*\n[\d.]+%\s*\n\s*Purchased/);
  if(purchasedMatch) stats.purchased = purchasedMatch[1];
  var convMatch = statsText.match(/([\d.]+%)\s*\n\s*Shop Conversion/);
  if(convMatch) stats.conversionRate = convMatch[1];

  // Referrers
  var refSection = statsText.match(/Top 10 Referrers\n([\s\S]*?)Creator Dashboard/);
  stats.referrers = refSection ? refSection[1].trim() : '';

  var totalMatch = statsText.match(/Displaying events \d+-\d+ of (\d+)/);
  stats.totalEvents = totalMatch ? totalMatch[1] : '0';

  return JSON.stringify({events: events, stats: stats});
})()