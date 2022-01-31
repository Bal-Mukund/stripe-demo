import os,stripe,uvicorn
from stripe import error
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

class Customers(BaseModel):
    name:str
    email:Optional[str]
    description:Optional[str]
    address:Optional[str]

app=FastAPI(title="Stripe Payment Demo")

templates=Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"),name="static")

stripe.api_key=os.environ["STRIPE_KEY"]
# stripe.api_key="sk_test_51JQnzHSCDB2sPH6iDRL16h6sTgKFdz2VLcpBuhrCulCff2wdobRkdL0eTtuS43uic35RzsxkPi0szZqGNOIyBHBD0037uG9JMI"
# This is a terrible index idea, only used for demo purposes!
app.state.stripe_customer_id = None

@app.get("/products",tags=["products"])
def get_all_products():
    return stripe.Product.list()

@app.get("/product/{prod_id}",tags=["products"])
def get_product_by_id(prod_id:str):
    product=stripe.Product.retrieve(prod_id)
    return product

@app.post("/products",status_code=201,tags=["products"])
def create_products(name:str):
    product=stripe.Product.create(name=name)
    return product

@app.delete("/product/{prod_id}",tags=["products"],status_code=204)
def delete_product(prod_id:str):
    return stripe.Product.delete(prod_id)

@app.post("/price/{prod_id}",status_code=201,tags=["products"])
def create_prices(prod_id:str,amount:int,currency:str):
    if currency.lower()!='inr':
        raise HTTPException(status_code=400,detail="Only Indian currency allowed!!")
    price = stripe.Price.create(
        unit_amount=amount,
        currency="inr",
        recurring={"interval": "month"},
        product=prod_id,
    )
    return price

@app.get("/prices",tags=["products"])
def get_all_prices():
    prices=stripe.Price.list()
    if prices==[]:
        raise HTTPException(status_code=404,detail="No prices found!!")
    return prices

@app.get("/price/{price_id}",tags=["products"])
def get_price_by_id(price_id:str):
    price=stripe.Price.retrieve(price_id)
    for i in stripe.Price.list().data:
        if price_id ==i.id:
            return price
    raise HTTPException(status_code=404,detail=f"Price with price_id: {price_id} does not exist!!")

# @app.delete("/price/{price_id}",tags=["products"],status_code=204)
# def delete_price(price_id:str):
#     return stripe.Price.delete(price_id)

# customers

@app.get("/customers",tags=["customers"])
def get_all_customers():
    return stripe.Customer.list()

@app.get("/customers/{cust_id}",tags=["customers"])
def get_customer_by_id(cust_id:str):
    customer=stripe.Customer.retrieve(cust_id)
    if customer == {}:
        raise HTTPException(status_code=404,detail=f"Customer with id: {cust_id} does not exist!!")
    return customer

@app.post("/customers",tags=["customers"],status_code=201)
def create_customers(name:str,email:Optional[str]):
    customer_created=stripe.Customer.create(name=name,email=email)
    return customer_created

@app.delete("/customer/{cust_id}",tags=["customers"],status_code=204)
def delete_customer(cust_id:str):
    return stripe.Customer.delete(cust_id)

# payment process

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "hasCustomer": app.state.stripe_customer_id is not None})

# @app.get("/")
# def index(request: Request):
#     html_content="""
#     <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Stripe Subscription</title>
#     <script src="https://js.stripe.com/v3/"></script>
#     <link href="https://github.com/PrettyPrinted/youtube_video_code/blob/master/2020/06/12/Accepting%20Payments%20in%20Flask%20Using%20Stripe%20Checkout%20%5B2020%5D/flask_stripe/static/narrow-jumbotron.css" rel="stylesheet" type="text/css">
#     <link href="https://github.com/PrettyPrinted/youtube_video_code/blob/master/2020/06/12/Accepting%20Payments%20in%20Flask%20Using%20Stripe%20Checkout%20%5B2020%5D/flask_stripe/static/bootstrap.min.css" rel="stylesheet" type="text/css">
# <link href="https://stripe-samples.github.io/developer-office-hours/demo.css" rel="stylesheet" type="text/css">
# </head>
# <body>
#     <div id="main">
#       <div id="container">
#         <div id="panel">
#              <br><br>
#           <h1>Products Available</h1>
#             <br><br><br>
#             """
#     products=stripe.Product.list()
#     # c=0
#     for i in products:
#         price=stripe.Price.list(product=i.id)
#         price_id=price.data[0].id
#         html_content+="""<h4>Product ID: """+i.id+"""</h4>
#         <h4>Product Name: """+i.name+"""</h4>
#                <button id='"""+i.id+"""'>Subscribe</button> <br><br><br>
#                 <script charset="utf-8">
#         var createCheckoutSession = function(priceId) {
#         return fetch("/create-checkout-session", {
#           method: "POST",
#           headers: {
#             "Content-Type": "application/json"
#           },
#           body: JSON.stringify({
#             priceId: priceId
#           })
#         }).then(function(result) {
#           return result.json();
#         });
#         };
#
#         const PREMIUM_PRICE_ID ='"""+price_id+"""';
#         const BASIC_PRICE_ID = "price_1KMSNbSAOUeH5vX2eMPPJc8A";
#         const stripe = Stripe("pk_test_51KI9haSAOUeH5vX2Cg1aMbrlN24uf6P0HXLAG0mfoFroTJlKCzc5W2P03YGWM9SHKx3tz16eryKVXKMKkHHJs4fV00Rna9EJrE");
#
#         document.addEventListener("DOMContentLoaded", function(event) {
#             document
#             .getElementById('"""+i.id+"""')
#             .addEventListener("click", function(evt) {
#                 createCheckoutSession(PREMIUM_PRICE_ID).then(function(data) {
#                     stripe
#                         .redirectToCheckout({
#                             sessionId: data.sessionId
#                         });
#                     });
#                 });
#
#             document
#             .getElementById("checkout-basic")
#             .addEventListener("click", function(evt) {
#                 createCheckoutSession(BASIC_PRICE_ID).then(function(data) {
#                     stripe
#                         .redirectToCheckout({
#                             sessionId: data.sessionId
#                         });
#                     });
#                 });
#
#             const billingButton = document.getElementById("manage-billing");
#             if (billingButton) {
#                 billingButton.addEventListener("click", function(evt) {
#                 fetch("/create-portal-session", {
#                     method: "POST"
#                 })
#                     .then(function(response) {
#                         return response.json()
#                     })
#                     .then(function(data) {
#                         window.location.href = data.url;
#                     });
#                 })
#             }
#         });
#
#         </script>
#         """
#     html_content+="""
#         </div>
#       </div>
#     </div>
#
# </body>
# </html>
#
#     """
#     return HTMLResponse(content=html_content)


@app.get("/success")
async def success(request:Request):
    return templates.TemplateResponse("success.html",{"request":request})

@app.get("/cancel")
async def cancel(request:Request):
    return templates.TemplateResponse("cancel.html",{"request":request})

@app.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()

    if not app.state.stripe_customer_id:
        customer = stripe.Customer.create(
            description="Demo customer",
        )
        app.state.stripe_customer_id = customer["id"]

    checkout_session = stripe.checkout.Session.create(
        customer=app.state.stripe_customer_id,
        success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:8000/cancel",
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": data["priceId"],
            "quantity": 1
        }],
    )
    return {"sessionId": checkout_session["id"]}


# @app.post("/create-portal-session")
# async def create_portal_session():
#     session = stripe.billing_portal.Session.create(
#         customer=app.state.stripe_customer_id,
#         return_url="http://localhost:8000"
#     )
#     return {"url": session.url}

if __name__=="__main__":
    uvicorn.run("app:app",reload=True)