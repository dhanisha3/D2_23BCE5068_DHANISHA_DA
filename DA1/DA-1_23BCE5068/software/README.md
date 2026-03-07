# 🔐 Secure Locker System

A comprehensive smart delivery locker system with QR code authentication, real-time analytics, and dynamic locker management.

## 📊 Project Status: Phase 1 Complete (50%)

### ✅ Phase 1 - Frontend UI (Completed)
- Dashboard interface with locker status display
- Ecommerce portal UI for creating deliveries
- Delivery agent portal UI for parcel deposit
- Customer portal UI for parcel pickup
- Responsive design with dark theme
- Real-time status indicators and animations
- Multi-portal navigation system

### 🔲 Phase 2 - Backend & QR System (Planned)
- [ ] SQLite database implementation
- [ ] QR code generation using qrcode library
- [ ] Secure token generation (UUID-based)
- [ ] Delivery lifecycle management  
- [ ] Agent deposit workflow
- [ ] Customer pickup workflow
- [ ] Access logging & audit trail
- [ ] Delivery analytics & reporting
- [ ] REST API endpoints
- [ ] Phone number validation
- [ ] QR code expiration system
- [ ] Testing suite

## ✨ Features

### 🎯 Core Functionality (Planned)
- **QR Code Authentication**: Secure agent and customer access
- **Dynamic Locker Management**: Real-time availability tracking
- **Multi-Portal Interface**: Separate interfaces for ecommerce, agents, and customers
- **Real-time Analytics**: Live delivery statistics and performance metrics

### 🎨 UI Features (Implemented)
- **Dark Theme**: Professional dark card design
- **Responsive Layout**: Works on all device sizes  
- **Interactive Elements**: Hover effects and animations
- **Visual Feedback**: Color-coded status indicators
- **Multi-Portal Navigation**: Dashboard, Ecommerce, Agent, Customer portals

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd secure-locker-system
   pip install flask
   ```

2. **Start Web Application**
   ```bash
   python web_app.py
   ```

3. **Access Portals**
   - Dashboard: http://localhost:5001/
   - Ecommerce: http://localhost:5001/ecommerce
   - Agent: http://localhost:5001/agent
   - Customer: http://localhost:5001/customer

> **Note**: Currently running in frontend-only mode with mock data. Backend integration planned for Phase 2.

## 📱 Portal Guide

### 📊 Dashboard
**Purpose**: Monitor system status and locker availability

**Features (UI Implemented)**:
- Real-time locker status display
- System statistics cards
- Quick action buttons

### 🛒 Ecommerce Portal
**Purpose**: Create new deliveries and generate QR codes

**Features (UI Implemented)**:
- Delivery creation form with customer details
- Locker selection interface
- Package size and priority options

**Planned (Phase 2)**:
- QR code generation and display
- Phone number validation
- Real locker availability checking

### 🚚 Agent Portal
**Purpose**: Deposit parcels using agent QR codes

**Features (UI Implemented)**:
- QR code scanning interface
- Locker status display
- Deposit workflow steps

**Planned (Phase 2)**:
- QR token verification
- Locker state management
- Access logging

### 👤 Customer Portal
**Purpose**: Collect parcels using customer QR codes

**Features (UI Implemented)**:
- QR code scanning interface
- Pickup workflow steps

**Planned (Phase 2)**:
- Customer QR verification
- Pickup confirmation
- Delivery completion

## 🔧 System Architecture

### Database Schema (Planned for Phase 2)
```sql
-- Lockers table
CREATE TABLE lockers (
    locker_id TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    status TEXT DEFAULT 'available',
    total_deliveries INTEGER DEFAULT 0,
    last_used TIMESTAMP
);

-- Deliveries table
CREATE TABLE deliveries (
    delivery_id TEXT PRIMARY KEY,
    customer_phone TEXT NOT NULL,
    customer_email TEXT,
    locker_id TEXT NOT NULL,
    agent_qr TEXT NOT NULL,
    customer_qr TEXT NOT NULL,
    status TEXT DEFAULT 'pending_delivery',
    priority TEXT DEFAULT 'standard',
    package_size TEXT DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    deposited_at TIMESTAMP,
    picked_up_at TIMESTAMP
);

-- Access logs table
CREATE TABLE access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    locker_id TEXT,
    delivery_id TEXT,
    role TEXT,
    action TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Delivery States (Planned)
1. **pending_delivery**: QR codes generated, waiting for agent
2. **deposited**: Agent deposited parcel, waiting for customer
3. **ready_for_pickup**: Customer can collect parcel
4. **picked_up**: Delivery completed successfully

### Locker States (Planned)
- **available**: Ready for new deliveries
- **depositing**: Agent is placing parcel
- **occupied**: Contains parcel waiting for pickup
- **pickup**: Customer is collecting parcel

## 📁 Project Structure

```
secure-locker-system/
├── web_app.py          # Flask web server (serves frontend with mock data)
├── main.py             # Core classes (stubbed - Phase 2)
├── db.py               # Database module (stubbed - Phase 2)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── templates/
    ├── base.html       # Base template with navigation
    ├── index.html      # Dashboard template
    ├── ecommerce.html  # Ecommerce portal template
    ├── agent.html      # Agent portal template
    └── customer.html   # Customer portal template
```

## 🎯 Future Enhancements (Beyond Phase 2)

- **Mobile App**: Native iOS/Android applications
- **SMS Integration**: Automatic SMS notifications
- **Email Notifications**: Delivery status updates
- **Multi-location Support**: Manage multiple locker sites
- **Advanced Analytics**: Machine learning insights
- **IoT Integration**: Hardware locker connectivity

---

**Built with ❤️ for secure, efficient package delivery**