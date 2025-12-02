import { ErrorBoundary } from "@/errors";
import { route as homeRoute } from "@/home"
import { ProtectedLayout, protectedLoader } from "@/layouts";
import { route as loginRoute } from "@/login"
import { route as logoutRoute } from "@/logout"
import { createBrowserRouter, redirect, type RouteObject } from "react-router"

const RootComponent = () => <br />

// Redirect to /home which will redirect to /login if necessary
const rootLoader = () => {
  return redirect("/home")
}

const rootRoute: RouteObject = {
  path: "/",
  loader: rootLoader,
  ErrorBoundary,
  index: true,
  Component: RootComponent,
}

export const router = createBrowserRouter([
  rootRoute,
  loginRoute,
  {
    // No path because it is a layout, not a parent page.
    path: undefined,
    Component: ProtectedLayout,
    loader: protectedLoader,
    ErrorBoundary,
    children: [
      homeRoute,
      logoutRoute,
      // TODO: settingsRoute
      // TODO: historyRoute
    ],
  }
])
