var createCheckoutSession = function(priceId) {
    return fetch("/create-checkout-session", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        priceId: priceId
      })
    }).then(function(result) {
      return result.json();
    });
  };

const PREMIUM_PRICE_ID = "price_1KMHalSGqKgAohxdsh9zT4eh";
const PREMIUM_PRICE_ID1="price_1KMHalSGqKgAohxdsh9zT4eh";
const BASIC_PRICE_ID = "price_1KMHa7SGqKgAohxdN8PDIxmC";
const BASIC_PRICE_ID1="price_1KMHa7SGqKgAohxdN8PDIxmC";
const stripe = Stripe("pk_test_51ImNI8SGqKgAohxdFnn4YOa9q40ihqk9DTxAjRGwUlxBcT8YHSXMbdwqBS3P1ufAEn1ZN9SreQdazWuODliY9KZy00aNeayavo");

document.addEventListener("DOMContentLoaded", function(event) {
    document
    .getElementById("checkout-premium")
    .addEventListener("click", function(evt) {
        createCheckoutSession(PREMIUM_PRICE_ID).then(function(data) {
            stripe
                .redirectToCheckout({
                    sessionId: data.sessionId
                });
            });
        });

    document
    .getElementById("checkout-basic")
    .addEventListener("click", function(evt) {
        createCheckoutSession(BASIC_PRICE_ID).then(function(data) {
            stripe
                .redirectToCheckout({
                    sessionId: data.sessionId
                });
            });
        });

    const billingButton = document.getElementById("manage-billing");
    if (billingButton) {
        billingButton.addEventListener("click", function(evt) {
        fetch("/create-portal-session", {
            method: "POST"
        })
            .then(function(response) {
                return response.json()
            })
            .then(function(data) {
                window.location.href = data.url;
            });
        })
    }
});
