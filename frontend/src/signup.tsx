import axios from "axios";
import { type ActionFunctionArgs, type RouteObject, redirect, Link, useFetcher, useSearchParams } from 'react-router'
import * as z from "zod";

import { Button } from '@/components/ui/button'
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getBackendURL } from '@/url';

const parseSignUpForm = (formData: FormData) => {
    console.log(formData)
    const signUpFormSchema = z.object({
        username: z.string(),
        password: z.string(),
        "repeat-password": z.string(),
    }).refine((data) => data.password === data["repeat-password"], {
        message: "Passwords don't match",
        path: ["repeat-password"], // path of error
    });
    const { data: parsedFormData, error } = signUpFormSchema.safeParse({
        password: formData.get('password'),
        username: formData.get('username'),
        "repeat-password": formData.get('repeat-password'),
    })
    if (error) throw error
    return parsedFormData
}

const action = async ({ request }: ActionFunctionArgs) => {
    const formData = await request.formData()
    const parsedFormData = parseSignUpForm(formData)

    const url = getBackendURL()
    try {
        await axios.post(
            `${url}/api/users`,
            JSON.stringify(parsedFormData),
            { headers: { "Content-Type": "application/json" } }
        )
        return redirect('/sign-up?success')
    } catch {
        return {
            error: 'An error occurred',
        }
    }
}


export const Page = () => {
    const fetcher = useFetcher<typeof action>()
    const [searchParams] = useSearchParams()

    const success = !!searchParams.has('success')
    const error = fetcher.data?.error
    const loading = fetcher.state === 'submitting'

    const formFields: { label: ReturnType<typeof Label>, input: ReturnType<typeof Input> }[] = [
        {
            label: <Label htmlFor="username">Username</Label>,
            input: <Input id="username" name="username" type="text" minLength={4} maxLength={20} required />
        },
        {
            label: <Label htmlFor="password">Password</Label>,
            input: <Input id="password" name="password" type="password" required />
        },
        {
            label: <Label htmlFor="repeat-password">Repeat Password</Label>,
            input: <Input id="repeat-password" name="repeat-password" type="password" required />
        }
    ]

    return (
        <div className="flex min-h-svh w-full items-center justify-center p-6 md:p-10">
            <div className="w-full max-w-sm">
                <div className="flex flex-col gap-6">
                    {success ?
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-2xl">Sign up successful</CardTitle>
                                <CardDescription className="text-sm text-muted-foreground">
                                    You can now <Link to="/login" className="underline underline-offset-4">
                                        log in
                                    </Link> using your username and password.
                                </CardDescription>
                            </CardHeader>
                        </Card> :
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-2xl">Sign up</CardTitle>
                                <CardDescription>Create a new account</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <fetcher.Form method="post" className="flex flex-col gap-6">
                                    {formFields.map((field, i) => <div className="grid gap-2" key={i}>
                                        {field.label}
                                        {field.input}
                                    </div>)}
                                    {error && <p className="text-sm text-red-500">{error}</p>}

                                    <Button type="submit" className="w-full" disabled={loading}>
                                        {loading ? 'Creating an account...' : 'Sign up'}
                                    </Button>
                                    <div className="text-center text-sm">
                                        Already have an account?{' '}
                                        <Link to="/login" className="underline underline-offset-4">
                                            Login
                                        </Link>
                                    </div>
                                </fetcher.Form>
                            </CardContent>
                        </Card>}
                </div>
            </div>
        </div>
    )
}


export const route: RouteObject = {
    path: 'sign-up',
    Component: Page,
    action,
}
