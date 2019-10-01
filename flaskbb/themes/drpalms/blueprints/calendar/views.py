from flask import (
  Blueprint,
  current_app,
  render_template,
  url_for,
  request,
  redirect,
  flash,
)

from flask_login import login_required, current_user
from flask_babel import gettext as _

from config import settings
from lib.util_json import render_json
from snakeeyes.blueprints.billing.forms import SubscriptionForm, \
    UpdateSubscriptionForm, CancelSubscriptionForm, PaymentForm
from snakeeyes.blueprints.billing.models.coupon import Coupon
from snakeeyes.blueprints.billing.models.subscription import Subscription
from snakeeyes.blueprints.billing.models.invoice import Invoice
from snakeeyes.blueprints.billing.decorators import subscription_required, \
    handle_stripe_exceptions

billing = Blueprint('billing', __name__, template_folder='../templates',
                    url_prefix='/subscription')


@billing.route('/pricing')
def pricing():
    if current_user.is_authenticated and current_user.subscription:
        return redirect(url_for('billing.update'))

    form = UpdateSubscriptionForm()

    return render_template('billing/pricing.html', form=form,
                           plans=settings.STRIPE_PLANS)


@billing.route('/coupon_code', methods=['POST'])
@login_required
def coupon_code():
    code = request.form.get('coupon_code')
    if code is None:
        return render_json(422,
                           {'error': 'Coupon code cannot be processed.'})

    coupon = Coupon.find_by_code(code)
    if coupon is None:
        return render_json(404, {'error': 'Coupon code not found.'})

    return render_json(200, {'data': coupon.to_json()})
