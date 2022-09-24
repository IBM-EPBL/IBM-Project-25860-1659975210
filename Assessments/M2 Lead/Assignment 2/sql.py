from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
username = "esvar"
password = "622001"
with sql.connect("student_database.db") as con:
          cur = con.cursor()
statement = f"SELECT name from students WHERE name='{username}' AND Pin= '{password}';"
cur.execute(statement)
if not cur.fetchone():  # An empty result evaluates to False.
    print("Login failed")
else:
    print("Welcome")



