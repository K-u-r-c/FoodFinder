let autocomplete;

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById("id_address"),
        {
            types: ["geocode", "establishment"],
            componentRestrictions: {country: ["pl"]},
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

    geocoder.geocode({address: address}, function (results, status) {
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
                    applyCartAmount(
                        response.cart_amount["subtotal"],
                        response.cart_amount["tax_dict"],
                        response.cart_amount["total"]
                    );
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
        cart_id = $(this).attr("id");
        url = $(this).attr("data-url");

        $.ajax({
            type: "GET",
            url: url,
            success: function (response) {
                // console.log(response);
                if (response.success) {
                    $("#cart_counter").html(response.cart_counter["cart_count"]);
                    $("#qty-" + food_id).html(response.cart_item_quantity);
                    removeCartItem(response.cart_item_quantity, cart_id);
                    applyCartAmount(
                        response.cart_amount["subtotal"],
                        response.cart_amount["tax_dict"],
                        response.cart_amount["total"]
                    );
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
                    applyCartAmount(
                        response.cart_amount["subtotal"],
                        response.cart_amount["tax_dict"],
                        response.cart_amount["total"]
                    );

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
        if (window.location.pathname == "/cart/") {
            if (cartItemQuantity <= 0) {
                $("#cart-item-" + cartId).remove();
            }
            checkEmptyCart();
        }
    }

    // check if cart is empty
    function checkEmptyCart() {
        var cartCounter = document.getElementById("cart_counter").innerHTML;
        if (cartCounter <= 0) {
            document.getElementById("empty-cart").style.display = "block";
        }
    }

    // apply cart amount
    function applyCartAmount(subtotal, tax_dict, total) {
        if (window.location.pathname == "/cart/") {
            $("#subtotal").html(subtotal);
            $("#total").html(total);

            for (key1 in tax_dict) {
                for (key2 in tax_dict[key1]) {
                    $("#tax-" + key1).html(tax_dict[key1][key2]);
                }
            }
        }
    }

    // place cart item quantity on load
    $(".item_qty").each(function () {
        var id = $(this).attr("id");
        var qty = $(this).attr("data-qty");
        $("#" + id).html(qty);
    });

    // add opening hour
    $(".add_hour").on('click', function (e) {
        e.preventDefault();
        let day = document.getElementById("id_day").value;
        let from_hour = document.getElementById("id_from_hour").value;
        let to_hour = document.getElementById("id_to_hour").value;
        let is_closed = document.getElementById("id_is_closed").checked;
        let csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
        let url = document.getElementById("add_hour_url").value;

        let condition;
        if (is_closed) {
            is_closed = "True"
            condition = "day !== ''"
        } else {
            is_closed = "False"
            condition = "day !== '' && from_hour !== '' && to_hour !== ''"
        }

        if (eval(condition)) {
            $.ajax({
                type: "POST",
                url: url,
                data: {
                    day: day,
                    from_hour: from_hour,
                    to_hour: to_hour,
                    is_closed: is_closed,
                    csrfmiddlewaretoken: csrf_token,
                },
                success: function (response) {
                    if (response.success) {
                        let html;
                        if (response.is_closed) {
                            html = "<tr id='hour-"
                                + response.id
                                + "'><td><b>"
                                + response.day
                                + "</b></td><td> Closed </td><td><a href='#' class='remove_hour' data-url='/vendor/openingHours/remove/"
                                + response.id + "'>Remove</a></td></tr>";
                        } else {
                            html = "<tr id='hour-"
                                + response.id
                                + "'><td><b>"
                                + response.day
                                + "</b></td><td>"
                                + response.from_hour
                                + " - "
                                + response.to_hour
                                + "</td><td><a href='#' class='remove_hour' data-url='/vendor/openingHours/remove/"
                                + response.id + "'>Remove</a></td></tr>";
                        }

                        $(".opening_hours").append(html);
                        document.getElementById("opening_hours").reset();
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
            })
        } else {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Please fill all the fields!",
                confirmButtonColor: "#c33332",
            });
        }
    });

    // remove opening hour
    $(document).on('click', '.remove_hour', function (e) {
        e.preventDefault();
        let url = $(this).attr("data-url");

        $.ajax({
            type: "GET",
            url: url,
            success: function (response) {
                if (response.success) {
                    $("#hour-" + response.id).remove();
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
        })
    });

    // document ready end
});
