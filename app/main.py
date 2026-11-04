from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import Base, SessionLocal, engine, get_db
from app.models import Order
from app.schemas import AccountCreate, AccountOut, CategoryOut, ItemOut, OrderCreate, OrderOut, ProductOut
from app.security import create_access_token, get_current_username
from app.seed import seed_database
from app.services import AccountService, CatalogService, OrderService


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(
    title="JPetStore-6 Modernized (AI-Native Python Edition)",
    version="2.0.0",
    description="Modernized Python/FastAPI port of mybatis/jpetstore-6",
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "legacy_source": "mybatis/jpetstore-6"}


# --- Auth & Account Endpoints ---
@app.post("/api/v1/auth/token", tags=["Identity"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = AccountService.authenticate(db, form_data.username, form_data.password)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_access_token(username), "token_type": "bearer"}


@app.post("/api/v1/auth/register", response_model=AccountOut, status_code=201, tags=["Identity"])
def register(payload: AccountCreate, db: Session = Depends(get_db)):
    return AccountService.register_account(db, payload)


@app.get("/api/v1/accounts/me", response_model=AccountOut, tags=["Identity"])
def get_my_account(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    return AccountService.get_account(db, username)


# --- Catalog Endpoints ---
@app.get("/api/v1/categories", response_model=list[CategoryOut], tags=["Catalog"])
def get_categories(db: Session = Depends(get_db)):
    return CatalogService.list_categories(db)


@app.get("/api/v1/categories/{catid}/products", response_model=list[ProductOut], tags=["Catalog"])
def get_products_by_category(catid: str, db: Session = Depends(get_db)):
    return CatalogService.list_products_by_category(db, catid)


@app.get("/api/v1/products/search", response_model=list[ProductOut], tags=["Catalog"])
def search_products(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return CatalogService.search_products(db, q)


@app.get("/api/v1/products/{productid}/items", response_model=list[ItemOut], tags=["Catalog"])
def get_items_by_product(productid: str, db: Session = Depends(get_db)):
    return CatalogService.list_items_by_product(db, productid)


@app.get("/api/v1/items/{itemid}", response_model=ItemOut, tags=["Catalog"])
def get_item(itemid: str, db: Session = Depends(get_db)):
    return CatalogService.get_item(db, itemid)


# --- Order & Checkout Endpoints ---
@app.post("/api/v1/orders", response_model=OrderOut, status_code=201, tags=["Orders"])
def place_order(
    payload: OrderCreate,
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
):
    return OrderService.create_order(db, username, payload)


@app.get("/api/v1/orders", response_model=list[OrderOut], tags=["Orders"])
def list_my_orders(username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.userid == username).all()
    return [OrderOut.model_validate(o) for o in orders]


# --- Interactive Storefront UI for Live Demonstration ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def storefront_ui():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>JPetStore 6 — Modernized Python Edition</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen">
  <header class="bg-slate-900 text-white px-6 py-4 flex justify-between items-center shadow">
    <div>
      <h1 class="text-xl font-bold tracking-tight">🐾 JPetStore 6 <span class="text-emerald-400 text-sm font-normal">Python/FastAPI Modernized</span></h1>
      <p class="text-xs text-slate-400">Legacy Parity: Catalog • Search • Auth (j2ee/j2ee) • ACID Order Checkout</p>
    </div>
    <div class="flex items-center gap-3">
      <span id="authStatus" class="text-xs bg-slate-800 px-3 py-1.5 rounded">Not Signed In</span>
      <button onclick="loginDemo()" class="bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold px-3 py-1.5 rounded">One-Click Login (j2ee)</button>
      <a href="/docs" target="_blank" class="bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold px-3 py-1.5 rounded">Swagger / OpenAPI</a>
    </div>
  </header>

  <main class="max-w-6xl mx-auto p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
    <section class="md:col-span-2 space-y-4">
      <div class="bg-white p-4 rounded-lg shadow-sm border flex gap-2">
        <input id="searchInput" type="text" placeholder="Search products (e.g., Shark, Bulldog, Parrot)..." class="border rounded px-3 py-1.5 w-full text-sm" />
        <button onclick="searchProducts()" class="bg-slate-800 text-white px-4 py-1.5 rounded text-sm">Search</button>
      </div>
      <div id="categoriesBar" class="flex gap-2 flex-wrap"></div>
      <div id="catalogGrid" class="bg-white p-4 rounded-lg shadow-sm border min-h-[300px]"></div>
    </section>

    <aside class="space-y-4">
      <div class="bg-white p-4 rounded-lg shadow-sm border">
        <h2 class="font-bold text-base mb-2">🛒 Shopping Cart</h2>
        <div id="cartItems" class="text-sm text-slate-600 space-y-2 mb-3">Cart is empty</div>
        <button onclick="checkout()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 rounded text-sm">Place Transactional Order</button>
      </div>
      <div class="bg-white p-4 rounded-lg shadow-sm border">
        <h2 class="font-bold text-base mb-2">📦 Order & Audit Log</h2>
        <pre id="orderLog" class="text-xs bg-slate-900 text-emerald-400 p-3 rounded overflow-x-auto max-h-60">Ready.</pre>
      </div>
    </aside>
  </main>

  <script>
    let token = null;
    let cart = {};

    async function init() {
      const res = await fetch('/api/v1/categories');
      const cats = await res.json();
      document.getElementById('categoriesBar').innerHTML = cats.map(c =>
        `<button onclick="loadCategory('${c.catid}')" class="px-3 py-1.5 bg-white border rounded shadow-sm hover:bg-slate-100 text-sm font-semibold">${c.name} (${c.catid})</button>`
      ).join('');
      loadCategory('FISH');
    }

    async function loadCategory(catid) {
      const res = await fetch(`/api/v1/categories/${catid}/products`);
      const prods = await res.json();
      renderProducts(prods, `Category: ${catid}`);
    }

    async function searchProducts() {
      const q = document.getElementById('searchInput').value;
      if (!q) return;
      const res = await fetch(`/api/v1/products/search?q=${encodeURIComponent(q)}`);
      renderProducts(await res.json(), `Search Results: "${q}"`);
    }

    async function renderProducts(prods, title) {
      let html = `<h3 class="font-bold text-sm text-slate-500 uppercase mb-3">${title}</h3><div class="space-y-3">`;
      for (const p of prods) {
        const iRes = await fetch(`/api/v1/products/${p.productid}/items`);
        const items = await iRes.json();
        html += `<div class="border rounded p-3"><div class="font-bold">${p.name} <span class="text-xs text-slate-400">(${p.productid})</span></div><div class="text-xs text-slate-500 mb-2">${p.descn}</div>`;
        html += items.map(i => `<div class="flex justify-between items-center bg-slate-50 p-2 rounded mt-1 text-sm">
          <span><b>${i.itemid}</b> - ${i.attr1} ($${i.listprice}) | Stock: <b>${i.quantity_available}</b></span>
          <button onclick="addToCart('${i.itemid}', ${i.listprice})" class="bg-slate-800 text-white text-xs px-2.5 py-1 rounded">+ Add</button>
        </div>`).join('') + `</div>`;
      }
      document.getElementById('catalogGrid').innerHTML = html + `</div>`;
    }

    function addToCart(itemid, price) {
      cart[itemid] = cart[itemid] ? { qty: cart[itemid].qty + 1, price } : { qty: 1, price };
      renderCart();
    }

    function renderCart() {
      const keys = Object.keys(cart);
      if (!keys.length) { document.getElementById('cartItems').innerHTML = 'Cart is empty'; return; }
      let total = 0;
      document.getElementById('cartItems').innerHTML = keys.map(k => {
        const sub = cart[k].qty * cart[k].price;
        total += sub;
        return `<div class="flex justify-between border-b pb-1"><span>${k} x ${cart[k].qty}</span><span>$${sub.toFixed(2)}</span></div>`;
      }).join('') + `<div class="font-bold flex justify-between pt-1"><span>Subtotal</span><span>$${total.toFixed(2)}</span></div>`;
    }

    async function loginDemo() {
      const form = new URLSearchParams({ username: 'j2ee', password: 'j2ee' });
      const res = await fetch('/api/v1/auth/token', { method: 'POST', body: form });
      const data = await res.json();
      token = data.access_token;
      document.getElementById('authStatus').innerText = 'Signed in as: j2ee';
      document.getElementById('orderLog').innerText = 'JWT issued for user j2ee.';
    }

    async function checkout() {
      if (!token) await loginDemo();
      const items = Object.keys(cart).map(k => ({ itemid: k, quantity: cart[k].qty }));
      if (!items.length) { alert('Add an item to cart first!'); return; }
      const res = await fetch('/api/v1/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ items })
      });
      const out = await res.json();
      document.getElementById('orderLog').innerText = JSON.stringify(out, null, 2);
      if (res.ok) { cart = {}; renderCart(); loadCategory('FISH'); }
    }

    init();
  </script>
</body>
</html>
"""