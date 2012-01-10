import os
import stripe

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

try:
    import settings
except ImportError, im:
    print "**** Yo Dawg!  You need to rename settings.py.example\n to settings.py and pop in your stripe keys"
    settings = None

app = Flask(__name__)

CURRENCY = 'usd'

@app.route("/", methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        try:
            amount = request.form['amount']
            email = request.form['email']
            token = request.form['token']
            
            #I'm sure there is a much better way but this is a 
            #demo so I can get away with it and I know this
            #is bad input validation :)
            
            #We do this because stripe charges in cents so 400 == 4.00 and 40000 == 400.00 neat
            if "." in amount:
                amount = int(amount.replace(".", ""))
            else:
                amount = int(amount) * 100
                
            customer  = stripe.Customer.create( email=email,
                                                description="Customer for %s" % email, 
                                                card=token)
        
            charge = stripe.Charge.create(amount=amount, currency=CURRENCY, customer=customer.id)
        
            flash("Charged %s cents to %s" % (amount, email), category='success')
        except Exception, ex:
            flash(ex.message, category='error')
    
    customers = stripe.Customer.all()
    charges = stripe.Charge.all()
    
    return render_template('index.html', customers=customers, charges=charges, settings=settings)

@app.route("/customers", methods=['GET', 'POST'])
def customers():
    customers = stripe.Customer.all()
    return render_template('customers.html', customers=customers, settings=settings)

@app.route("/charges", methods=['GET', 'POST'])
def charges():
    charges = stripe.Charge.all()
    return render_template('charges.html', charges=charges)

if __name__ == "__main__":
    if settings:
        port = int(os.environ.get("PORT", 5000))
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        app.secret_key = settings.SESSION_SECRET #session secret
        app.run(debug=True, host='0.0.0.0', port=port)
