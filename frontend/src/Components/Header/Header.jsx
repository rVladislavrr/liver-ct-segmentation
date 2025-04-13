import React from "react";
import { Link } from "react-router-dom";
import './Header.css'
const Header = () => {
    return (
        <div className="main-header">
            <div className="registration-header">
                <Link to='/login'>
                    <button className="header-login-button">Войти</button>
                </Link>
                <Link to='/registration'>
                    <button className="header-registration-button">Регистрация</button>
                </Link>
            </div>
        </div>
    );
}
 
export default Header;