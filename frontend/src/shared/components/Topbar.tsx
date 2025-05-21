import React, {useState} from "react";
import Searchbar from "./Searchbar";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBookBookmark, faHome, faRectangleList, faUser } from "@fortawesome/free-solid-svg-icons";

function Topbar() {
    const userSlug = localStorage.getItem('userSlug') || "";
    return (
    <div id="topbar">
      <div className="left">
        <a href="/">
          <button
            id="top-bar-home"
            className="menu-button"
          >
            <FontAwesomeIcon icon={faHome}/>
          </button>
        </a>
        <a href="/entries">
          <button
            id="top-bar-entries"
            className="menu-button"
          >
            <FontAwesomeIcon icon={faRectangleList} />
          </button>
        </a>
        <a href={`/users/${userSlug}/bookmarks`}>
          <button
            id="top-bar-bookmarks"
            className="menu-button"
          >
            <FontAwesomeIcon icon={faBookBookmark} />
          </button>
        </a>
      </div>
      <div className="right">
        <Searchbar/>
        < a href={`/users/${userSlug}/profile/`}>
          <button
            id="top-bar-profile"
            className="menu-button"
          >
            <FontAwesomeIcon icon={faUser} />
          </button>
        </a>
      </div>
    </div>
  );
};

export default Topbar;