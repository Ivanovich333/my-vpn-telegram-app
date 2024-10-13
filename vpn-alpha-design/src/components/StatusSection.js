import React from 'react';
import './StatusSection.css';

function StatusSection() {
    return (
        <div className="status-section">
            <div className="status connected">
                <div className="status-title">Connected</div>
                <div className="status-subtitle">Server: USA</div>
            </div>
            <div className="status">
                <div className="status-title">Disconnected</div>
                <div className="status-subtitle">No Connection</div>
            </div>
        </div>
    );
}

export default StatusSection;
