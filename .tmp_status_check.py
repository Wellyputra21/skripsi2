import traceback
try:
    from app import app, init_recommender
    init_recommender()
    c = app.test_client()
    r1 = c.get('/')
    r2 = c.get('/destination/riau-001')
    r3 = c.get('/destination/not-found-id')
    print(r1.status_code, r2.status_code, r3.status_code)
except Exception:
    traceback.print_exc()
