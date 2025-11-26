import {ErrorBoundary} from "@/errors";
import {getBackendURL} from "@/url";
import axios from "axios";
import {redirect, type RouteObject} from "react-router";

const loader = async () => {
  const url = getBackendURL()
  try {
    await axios.post(
      `${url}/api/logout`,
      undefined,
      {withCredentials: true}
    )
    return redirect('/login')
  } catch {
    throw Error("Error logging out")
  }
}

export const route: RouteObject = {
  path: "logout",
  loader: loader,
  ErrorBoundary,
}
