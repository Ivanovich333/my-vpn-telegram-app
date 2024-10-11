import React from 'react';
import './ServerList.css';

function ServerList() {
    return (
        <div className="server-list">
            <div className="server"><span>Server 1: USA</span></div>
            <div className="server"><span>Server 2: Germany</span></div>
            <div className="server"><span>Server 3: Japan</span></div>
        </div>
    );
}

export default ServerList;
