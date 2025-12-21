import { ErrorBoundary } from "@/errors";
import axios from "axios";
import { redirect, useNavigate } from "react-router";
import { getBackendURL } from "@/url";


export const action = async () => {

  const url = getBackendURL()
  try {
    await axios.post(
      `${url}/api/guest_sessions`,
    )
    return redirect('/home')
  } catch {
    return {
      error: 'An error occurred',
    }
  }
}

import { useFetcher } from "react-router";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react";

type ContinueAsGuestCardProps = {
  error?: string;
  loading: boolean;
  fetcher: ReturnType<typeof useFetcher>;
}

export const ContinueAsGuestCard = ({
  error, loading, fetcher,
}: ContinueAsGuestCardProps) => {
  const navigate = useNavigate()
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Einsingen</CardTitle>
              Continue as guest?
            </CardHeader>
            <CardContent>
              <fetcher.Form method="post">
                <CardDescription className="flex flex-col gap-6">
                  You will not be able to save your exercises.
                  {error && <p className="text-sm text-red-500">{error}</p>}
                  <span className="flex flex-row">
                    <Button type="button" variant="outline" onClick={() => navigate("/login")}>
                      <ChevronLeftIcon />Back to Login
                    </Button>
                    <span className="grow" id="spacer" />
                    <Button type="submit" variant="outline">
                      Continue as Guest<ChevronRightIcon />
                    </Button>
                  </span>
                </CardDescription>
              </fetcher.Form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export const ContinueAsGuestPage = () => {
  const fetcher = useFetcher<typeof action>()
  const error = fetcher.data?.error
  const loading = fetcher.state === 'submitting'
  return (
    <ContinueAsGuestCard fetcher={fetcher} error={error} loading={loading} />
  )
}

export const route = {
  path: "/continue_as_guest",
  Component: ContinueAsGuestPage,
  action,
  ErrorBoundary,
}

