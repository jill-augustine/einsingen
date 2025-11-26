import * as React from "react";
import {isRouteErrorResponse} from "react-router";
import {useRouteError} from "react-router-dom";

export const ErrorBoundary = () => {
  const error = useRouteError()
  console.error(error)
  if (isRouteErrorResponse(error)) {
    const message = error.status === 404 ? "404" : "Error";
    const details = error.status === 404 ?
      "The requested page could not be found." :
      "An unexpected error occurred."
    return <div>{message}: {details}<br/>Time for vocal rest?</div>
  }
}