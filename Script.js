// Mock data for demonstration
const inventoryData = [
    { id: 1, name: 'Product 1', quantity: 100 },
    { id: 2, name: 'Product 2', quantity: 50 },
    { id: 3, name: 'Product 3', quantity: 75 }
  ];
  
  const orderData = [
    { id: 1, customer: 'Customer A', products: ['Product 1', 'Product 2'], status: 'Pending' },
    { id: 2, customer: 'Customer B', products: ['Product 2', 'Product 3'], status: 'Shipped' }
  ];
  
  // Function to render inventory items
  function renderInventory() {
    const inventoryList = document.getElementById('inventory-list');
    inventoryList.innerHTML = '';
    inventoryData.forEach(item => {
      const li = document.createElement('li');
      li.textContent = `${item.name} - Quantity: ${item.quantity}`;
      inventoryList.appendChild(li);
    });
  }
  
  // Function to render order items
  function renderOrders() {
    const orderList = document.getElementById('order-list');
    orderList.innerHTML = '';
    orderData.forEach(order => {
      const li = document.createElement('li');
      li.textContent = `Order ID: ${order.id} - Customer: ${order.customer} - Status: ${order.status}`;
      orderList.appendChild(li);
    });
  }
  
  // Initial rendering
  renderInventory();
  renderOrders();
  