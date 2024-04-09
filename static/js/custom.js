let autocomplete;

function initAutoComplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
    {
      types: ["geocode", "establishment"],
      componentRestrictions: { country: ["pl"] },
    }
  );
  autocomplete.addListener("place_changed", onPlaceChanged);
}

function onPlaceChanged() {
  var place = autocomplete.getPlace();

  if (!place.geometry) {
    document.getElementById("id_address").placeholder = "Start typing...";
  }

  var geocoder = new google.maps.Geocoder();
  var address = document.getElementById("id_address").value;

  geocoder.geocode({ address: address }, function (results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      var lat = results[0].geometry.location.lat();
      var lng = results[0].geometry.location.lng();
      $("#id_latitude").val(lat);
      $("#id_longitude").val(lng);
      $("#id_address").val(address);
    }
  });

  for (var i = 0; i < place.address_components.length; i++) {
    for (var j = 0; j < place.address_components[i].types.length; j++) {
      if (place.address_components[i].types[j] === "country") {
        $("#id_country").val(place.address_components[i].long_name);
      }
      if (place.address_components[i].types[j] === "locality") {
        $("#id_city").val(place.address_components[i].long_name);
      }
      if (place.address_components[i].types[j] === "postal_code") {
        $("#id_pin_code").val(place.address_components[i].long_name);
      } else {
        $("#id_pin_code").val("");
      }
    }
  }
}

$(document).ready(function () {
  $(".add_to_cart").on("click", function (event) {
    event.preventDefault();

    food_id = $(this).attr("data-id");
    url = $(this).attr("data-url");
    data = {
      food_id: food_id,
    };

    $.ajax({
      type: "GET",
      url: url,
      data: data,
      success: function (response) {
        console.log(response);
        $("#cart_counter").html(response.cart_counter["cart_count"]);
        $("#qty-" + food_id).html(response.cart_item_quantity);
      },
    });
  });

  // Place cart item quantity on load
  $(".item_qty").each(function () {
    var id = $(this).attr("id");
    var qty = $(this).attr("data-qty");
    $("#" + id).html(qty);
  });
});
