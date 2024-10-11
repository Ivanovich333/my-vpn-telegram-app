import React from 'react';
import './Stats.css';

function Stats() {
    return (
        <div className="stats">
            <div className="stat">
                <div className="stat-title">Ping</div>
                <div>23 ms</div>
            </div>
            <div className="stat">
                <div className="stat-title">Speed</div>
                <div>36 Mbps</div>
            </div>
        </div>
    );
}

export default Stats;
