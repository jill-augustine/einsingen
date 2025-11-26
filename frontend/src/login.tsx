import {ErrorBoundary} from "@/errors";
import axios from "axios";
import {type ActionFunctionArgs, redirect} from "react-router";
import * as z from "zod";
import {getBackendURL} from "@/url";

const loginFormSchema = z.object({
  username: z.string(),
  password: z.string(),
});
type LoginFormData = z.infer<typeof loginFormSchema>

export const parseLoginForm = (formData: FormData): LoginFormData => {
  const {data: parsedFormData, error} = loginFormSchema.safeParse({
    username: formData.get('username'),
    password: formData.get('password'),
  })
  if (error) throw error
  return parsedFormData
}

export const action = async ({request}: ActionFunctionArgs) => {
  const formData = await request.formData()
  const parsedFormData = parseLoginForm(formData)

  const url = getBackendURL()
  try {
    await axios.post(
      `${url}/api/login`,
      `username=${parsedFormData.username}&password=${parsedFormData.password}`,
      {headers: {"Content-Type": "application/x-www-form-urlencoded"}}
    )
    return redirect('/home')
  } catch {
    return {
      error: 'An error occurred',
    }
  }
}

import {Link, useFetcher} from "react-router";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {Label} from "@/components/ui/label";
import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";

type LoginCardProps = {
  error?: string;
  loading: boolean;
  fetcher: ReturnType<typeof useFetcher>;
}

export const LoginCard = ({
                            error, loading, fetcher,
                            // testUserError, testUserLoading
                          }: LoginCardProps) => {
  return (
    <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Einsingen</CardTitle>
              An app for vocal warm-ups
            </CardHeader>
            <CardContent>
              <fetcher.Form method="post">
                <div className="flex flex-col gap-6">
                  <div className="grid gap-2">
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      name="username"
                      type="text"
                      placeholder=""
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <div className="flex items-center">
                      <Label htmlFor="password">Password</Label>
                      {/*  <Link*/}
                      {/*    to="/forgot-password"*/}
                      {/*    className="ml-auto inline-block text-sm underline-offset-4 hover:underline"*/}
                      {/*  >*/}
                      {/*    Forgot your password?*/}
                      {/*  </Link>*/}
                    </div>
                    <Input id="password" type="password" name="password" required/>
                  </div>
                  {error && <p className="text-sm text-red-500">{error}</p>}
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? 'Logging in...' : 'Login'}
                  </Button>
                </div>
              </fetcher.Form>
              {/*<div className="mt-4 text-center text-sm">*/}
              {/*  Don&apos;t have an account?{' '}*/}
              {/*  <Link to="/sign-up" className="underline underline-offset-4">*/}
              {/*    Sign up*/}
              {/*  </Link>*/}
              {/*</div>*/}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export const LoginPage = () => {
  const fetcher = useFetcher<typeof action>()
  const error = fetcher.data?.error
  const loading = fetcher.state === 'submitting'
  return (
    <LoginCard fetcher={fetcher} error={error} loading={loading}/>
  )
}

export const route = {
  path: "/login",
  Component: LoginPage,
  action,
  ErrorBoundary,
}

