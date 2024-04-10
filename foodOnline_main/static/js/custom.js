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
  // add to cart
  $(".add_to_cart").on("click", function (event) {
    event.preventDefault();

    food_id = $(this).attr("data-id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        // console.log(response);
        if (response.success) {
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          $("#qty-" + food_id).html(response.cart_item_quantity);
        } else {
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: response.error,
            confirmButtonColor: "#c33332",
          });
        }
      },
    });
  });

  // decrease from cart
  $(".decrease_cart").on("click", function (event) {
    event.preventDefault();

    food_id = $(this).attr("data-id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        // console.log(response);
        if (response.success) {
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          $("#qty-" + food_id).html(response.cart_item_quantity);
        } else {
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: response.error,
            confirmButtonColor: "#c33332",
          });
        }
      },
    });
  });

  // delete cart
  $(".delete_cart").on("click", function (event) {
    event.preventDefault();

    cart_id = $(this).attr("data-id");
    url = $(this).attr("data-url");

    $.ajax({
      type: "GET",
      url: url,
      success: function (response) {
        if (response.success) {
          $("#cart_counter").html(response.cart_counter["cart_count"]);
          removeCartItem(0, cart_id);
          checkEmptyCart();

          Swal.fire({
            icon: "success",
            title: "Success",
            text: response.success,
            confirmButtonColor: "#c33332",
          });
        } else {
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: response.error,
            confirmButtonColor: "#c33332",
          });
        }
      },
    });
  });

  // delete cart element if the qantity is 0
  function removeCartItem(cartItemQuantity, cartId) {
    if (cartItemQuantity <= 0) {
      $("#cart-item-" + cartId).remove();
    }
  }

  // check if cart is empty
  function checkEmptyCart() {
    var cartCounter = document.getElementById("cart_counter").innerHTML;
    if (cartCounter <= 0) {
      document.getElementById("empty-cart").style.display = "block";
    }
  }

  // place cart item quantity on load
  $(".item_qty").each(function () {
    var id = $(this).attr("id");
    var qty = $(this).attr("data-qty");
    $("#" + id).html(qty);
  });
});
