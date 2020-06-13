from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Your Email:', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


class SubscribeForm(FlaskForm):
    beta_code = StringField('', validators=[DataRequired()],
                            render_kw={"placeholder": "Enter beta testing code", "class": "form-control"})
    email = StringField('', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Your email address", "class": "form-control"})
    submit = SubmitField('Subscribe', render_kw={"class": "btn btn-outline-secondary", "type": "submit"})
