from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DateTimeField, DateField
from wtforms.validators import DataRequired



class LoginForm(FlaskForm):

    loginName = StringField("Name", validators=[DataRequired()])
    loginPwd = PasswordField("Password", validators=[DataRequired()] )
    loginSubmit = SubmitField("Submit")
    

class UserRegisterForm(FlaskForm):

    regCPF = StringField("CPF", validators=[DataRequired()])
    regName = StringField("Nome", validators=[DataRequired()])
    regEmail = StringField("E-mail", validators=[DataRequired()])
    regPhone = StringField("Telefone", validators=[DataRequired()])
    regPassword = StringField("Senha", validators=[DataRequired()])
    regDateRegister = DateField("Data")
    regState = StringField("Estado")
    regCity = StringField("Cidade")
    regAddress = StringField("Endereço")
    regZipCode = StringField("CEP")
    submit = SubmitField("Cadastrar")
