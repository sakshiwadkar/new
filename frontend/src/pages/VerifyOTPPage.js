import React, { useState } from 'react';
import axios from 'axios';

const VerifyOTPPage = ({ email: initialEmail }) => {
    const [email, setEmail] = useState(initialEmail || '');
    const [otp, setOtp] = useState('');
    const [otpVerified, setOtpVerified] = useState(false); // State to track whether OTP is verified

    const verifyOTP = () => {
        axios.post('http://127.0.0.1:5000/verify-otp', { email, otp })
            .then(response => {
                console.log(response);
                const { data } = response;
                if (data && data.message) {
                    // If OTP verification is successful, update state
                    setOtpVerified(true);
                    alert('OTP verified successfully. You can reset your password now.');
                } else {
                    alert('Invalid OTP. Please try again.');
                }
            })
            .catch(error => {
                console.error(error);
                alert('Failed to verify OTP. Please try again.');
            });
    };

    const onSubmit = (e) => {
        e.preventDefault();
        verifyOTP();
    };

    return (
        <div>
            {!otpVerified ? ( // Render OTP verification form only if OTP is not verified
                <div>
                    <h2>Verify OTP</h2>
                    <form onSubmit={onSubmit}>
                        <div className="form-group">
                            <label>Email:</label>
                            <input
                                type="email"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>OTP:</label>
                            <input
                                type="text"
                                value={otp}
                                onChange={e => setOtp(e.target.value)}
                                required
                            />
                        </div>
                        <button type="submit" className="btn btn-primary">Verify OTP</button>
                    </form>
                </div>
            ) : (
                // Render message or redirection logic after OTP verification
                <div>
                    <p>OTP verified successfully. You can reset your password now.</p>
                    {/* Add redirection logic or link to reset password page here */}
                </div>
            )}
        </div>
    );
};

export default VerifyOTPPage;
