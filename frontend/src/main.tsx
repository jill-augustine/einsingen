import {
  RouterProvider,
} from "react-router";

import {router} from "./routes";
import ReactDOM from "react-dom/client";

import "./index.css"

const root = document.getElementById("root");
if (!root) {
  throw new Error("root is missing");
}
ReactDOM.createRoot(root).render(
  <RouterProvider router={router}/>
);
