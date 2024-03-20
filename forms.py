from main import app

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DateTimeField 
from wtforms.validators import DataRequired




class LoginForm(FlaskForm):

    loginName    = StringField("Name", validators=[DataRequired()])
    loginPwd     = PasswordField("Password", validators=[DataRequired()] )
    loginSubmit  = SubmitField("Submit")
    


#Registro que qualquer usuario pode fazer 
class UserRegisterForm(FlaskForm):

    regCPF           =  StringField    ("CPF", validators=[DataRequired()])
    regName          =  StringField    ("Nome", validators=[DataRequired()])
    regEmail         =  StringField    ("E-mail", validators=[DataRequired()])
    regPhone         =  StringField    ("Telefone")
    regPassword      =  StringField    ("Senha", validators=[DataRequired()])    
    regDateRegister  =  DateTimeField  ("Data")
    regState         =  StringField    ("Estado")
    regCity          =  StringField    ("Cidade")
    regZipCode       =  StringField    ("CEP")