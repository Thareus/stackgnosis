import {useEffect, useState} from "react";
import {toast} from "./Toast";
import {api} from "api";

const ContextMenu = () => {
  const [menuStyle, setMenuStyle] = useState<{display: string, left: number, top: number}>({ display: "none", left: 0, top: 0 });

  useEffect(() => {
    const handleContextMenu = (event: MouseEvent) => {
      event.preventDefault();
      let left = event.pageX;
      let top = event.pageY;
      setMenuStyle({
        display: "block",
        left,
        top,
      });
    };

    const handleClick = () => {
      setMenuStyle((prev) => ({ ...prev, display: "none" }));
    };

    document.addEventListener("contextmenu", handleContextMenu);
    document.addEventListener("click", handleClick);

    return () => {
      document.removeEventListener("contextmenu", handleContextMenu);
      document.removeEventListener("click", handleClick);
    };
  }, []);

  const selection = window.getSelection();
  const selectedText = selection?.toString().trim();

  return (
    <div
      id="context-menu"
      style={{
        display: menuStyle.display,
        left: menuStyle.left,
        top: menuStyle.top,
        position: 'absolute',
        zIndex: 1000
      }}
    >
      {selectedText && (
        <div>
          <ul onClick={() => api.requestNewEntry(selectedText)}>
            <li>Request new entry for <br></br> "{selectedText}"</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ContextMenu;
