# 🔐 Secure Locker System

A comprehensive smart delivery locker system with QR code authentication, real-time analytics, and dynamic locker management.

## ✨ Features

### 🎯 Core Functionality
- **QR Code Authentication**: Secure agent and customer access
- **Dynamic Locker Management**: Real-time availability tracking
- **Multi-Portal Interface**: Separate interfaces for ecommerce, agents, and customers
- **Real-time Analytics**: Live delivery statistics and performance metrics
- **Phone Number Validation**: Indian mobile number format validation (10 digits, starts with 6/7/8/9)

### 🔒 Security Features
- **Unique QR Codes**: Each delivery gets unique agent and customer QR codes
- **Expiration System**: QR codes expire after 7 days
- **Access Logging**: Complete audit trail of all locker access
- **Locker State Management**: Prevents multiple deliveries in same locker

### 📊 Analytics & Monitoring
- **Real-time Dashboard**: Live system status and locker availability
- **Delivery Analytics**: Success rates, completion times, peak hours
- **Customer Satisfaction**: Calculated metrics based on delivery performance
- **Usage Statistics**: Locker utilization and system performance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask
- SQLite3
- qrcode library

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd secure-locker-system
   pip install flask qrcode[pil] sqlite3
   ```

2. **Initialize System**
   ```bash
   python init_system.py
   ```

3. **Start Web Application**
   ```bash
   python web_app.py
   ```

4. **Access Portals**
   - Dashboard: http://localhost:5001/
   - Ecommerce: http://localhost:5001/ecommerce
   - Agent: http://localhost:5001/agent
   - Customer: http://localhost:5001/customer

## 📱 Portal Guide

### 🛒 Ecommerce Portal
**Purpose**: Create new deliveries and generate QR codes

**Features**:
- Create delivery with customer details
- Phone number validation (10 digits, starts with 6/7/8/9)
- Select available lockers only
- Generate agent and customer QR codes
- Real-time analytics dashboard
- Add new lockers dynamically

**Workflow**:
1. Enter delivery ID and customer phone
2. Select available locker
3. Generate QR codes
4. Share agent QR with delivery partner
5. Send customer QR to customer

### 🚚 Agent Portal
**Purpose**: Deposit parcels using agent QR codes

**Features**:
- Scan agent QR code to open locker
- View all locker statuses
- Deposit parcel and secure locker
- Real-time locker availability

**Workflow**:
1. Scan/enter agent QR code
2. Select correct locker
3. Open locker for deposit
4. Place parcel inside
5. Close and secure locker

### 👤 Customer Portal
**Purpose**: Collect parcels using customer QR codes

**Features**:
- Scan customer QR code to open locker
- View available parcels
- Pickup instructions and guidance
- Complete delivery process

**Workflow**:
1. Scan/enter customer QR code
2. Select locker with your parcel
3. Open locker for pickup
4. Collect parcel
5. Close locker to complete delivery

### 📊 Dashboard
**Purpose**: Monitor system status and analytics

**Features**:
- Real-time locker status
- System statistics
- Recent activity timeline
- Quick action buttons

## 🔧 System Architecture

### Database Schema
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

### Delivery States
1. **pending_delivery**: QR codes generated, waiting for agent
2. **deposited**: Agent deposited parcel, waiting for customer
3. **ready_for_pickup**: Customer can collect parcel
4. **picked_up**: Delivery completed successfully

### Locker States
- **available**: Ready for new deliveries
- **depositing**: Agent is placing parcel
- **occupied**: Contains parcel waiting for pickup
- **pickup**: Customer is collecting parcel

## 🛡️ Security Measures

### QR Code Security
- **Unique Tokens**: UUID4 generation for each QR code
- **Role-based Access**: Separate QR codes for agents and customers
- **Expiration**: 7-day automatic expiration
- **Single Use**: QR codes become invalid after successful use

### Validation
- **Phone Numbers**: 10-digit Indian mobile format validation
- **Locker Availability**: Prevents double-booking
- **Input Sanitization**: All inputs validated and sanitized
- **Error Handling**: Comprehensive error messages and logging

### Access Control
- **Audit Trail**: Complete logging of all access attempts
- **IP Tracking**: Log IP addresses for security monitoring
- **User Agent Tracking**: Browser/device information logging

## 📈 Analytics Features

### Real-time Metrics
- **Today's Deliveries**: Count of deliveries created today
- **Completion Rate**: Percentage of successful deliveries
- **Average Delivery Time**: Time from deposit to pickup
- **Peak Hours**: Busiest delivery times
- **Customer Satisfaction**: Calculated satisfaction score

### Performance Monitoring
- **Locker Utilization**: Usage statistics per locker
- **Success Rates**: Delivery completion percentages
- **Response Times**: System performance metrics
- **Error Rates**: Failed delivery attempts

## 🔧 API Endpoints

### Analytics API
```
GET /api/analytics
Returns: Real-time delivery analytics and statistics
```

### Locker Management API
```
GET /api/lockers
Returns: Current status of all lockers

POST /api/add_locker
Body: {"locker_id": "LOC009", "location": "Address"}
Returns: Success/error message

POST /api/reset_locker/<locker_id>
Returns: Locker reset confirmation
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_locker_system.py
```

**Test Coverage**:
- Locker availability management
- Delivery creation and QR generation
- Complete delivery workflow
- Phone number validation
- Error handling and edge cases

## 🎨 UI Features

### Modern Design
- **Dark Theme**: Professional dark card design
- **Responsive Layout**: Works on all device sizes
- **Real-time Updates**: Live data refresh without page reload
- **Interactive Elements**: Hover effects and animations
- **Accessibility**: WCAG compliant design

### User Experience
- **Visual Feedback**: Color-coded status indicators
- **Progress Tracking**: Step-by-step delivery process
- **Error Messages**: Clear, actionable error descriptions
- **Loading States**: Visual feedback during operations
- **Notifications**: Toast notifications for user actions

## 🔄 Workflow Examples

### Complete Delivery Cycle
1. **Ecommerce**: Create delivery → Generate QR codes
2. **Agent**: Scan agent QR → Open locker → Deposit parcel → Close locker
3. **System**: Update status to "ready_for_pickup"
4. **Customer**: Scan customer QR → Open locker → Collect parcel → Close locker
5. **System**: Mark delivery complete → Free locker for next delivery

### Error Scenarios
- **Occupied Locker**: System prevents double-booking
- **Invalid QR**: Clear error message with guidance
- **Expired QR**: Automatic expiration handling
- **Wrong Locker**: Validation prevents incorrect access

## 🚀 Production Deployment

### Environment Setup
1. Set secure secret key in `web_app.py`
2. Configure database backup strategy
3. Set up SSL/HTTPS for production
4. Configure logging and monitoring
5. Set up automated backups

### Security Checklist
- [ ] Change default secret key
- [ ] Enable HTTPS
- [ ] Set up database encryption
- [ ] Configure access logging
- [ ] Set up monitoring alerts
- [ ] Regular security updates

## 📞 Support

For issues or questions:
1. Check the test suite results
2. Review error logs in the console
3. Verify database connectivity
4. Check locker availability status

## 🎯 Future Enhancements

- **Mobile App**: Native iOS/Android applications
- **SMS Integration**: Automatic SMS notifications
- **Email Notifications**: Delivery status updates
- **Multi-location Support**: Manage multiple locker sites
- **Advanced Analytics**: Machine learning insights
- **IoT Integration**: Hardware locker connectivity

---

**Built with ❤️ for secure, efficient package delivery**