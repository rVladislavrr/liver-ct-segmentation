import React from "react";
import './Header.css'
const Header = () => {
    return (
        <div className="main-header">
            <div className="registration-header">
                <button className="header-login-button">Войти</button>
                <button className="header-registration-button">Регистрация</button>
            </div>
        </div>
    );
}
 
export default Header;