import plotly.express as px

fig = px.pie(
    names=["Good", "Bad"],
    values=[10, 5],
)

print("SUCCESS")