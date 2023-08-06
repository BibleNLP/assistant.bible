let supabaseClient;

export async function getSupabaseClient() {
  if (!supabaseClient) {
        try {
            const { createClient } = supabase;

            const response = await fetch('/api/get-supabase-keys');
            const data = await response.json();

            // Use the fetched Supabase keys in your frontend code
            const supabaseUrl = data.supabaseUrl;
            const supabaseKey = data.supabaseKey;

            // Initialize the Supabase client with the fetched keys
            supabaseClient = createClient(supabaseUrl, supabaseKey);


        } catch (error) {
            console.error('Error fetching Supabase keys:', error);
        }
    }
  return supabaseClient;
}

export async function signIn(event, username, password, url){
    event.preventDefault(); // Prevent the default form submission
    console.log('loginForm submit');
    // Get the entered values from the login form
    

    try {
        // Call the Supabase auth.signIn function with the entered values
        let { data, error } = await supabaseClient.auth.signInWithPassword({
            email: username, // Assuming the username input accepts email addresses
            password: password,
        });

        // Handle the response from Supabase
        if (error) {
            console.error('Login error:', error);
        } else {
            console.log('Login successful!', data);
            // Store the access token in the browser's local storage
            const accessToken = data.session.access_token; // Assuming the access token is returned in the 'data' object
            localStorage.setItem('accessToken', accessToken);
            console.log('access token stored');
            window.location.replace(url);
        }
    } catch (error) {
        console.error('Login error:', error);
    }
}


export async function signUp(event, signupEmail, signupPassword, url){
    event.preventDefault(); // Prevent the default form submission
            try {
                // Call the Supabase auth.signIn function with the entered values
                let { data, error } = await supabaseClient.auth.signUp({
                    email: signupEmail, // Assuming the username input accepts email addresses
                    password: signupPassword,
                    options: {
                        data: {
                            'user_type': 'paratext'
                        },
                        emailRedirectTo: url
                        }
                });

                // Handle the response from Supabase
                if (error) {
                    console.error('Sign up error:', error);
                } else {
                    console.log('Sign up successful!', data);
                    const accessToken = data.session.access_token
                    localStorage.setItem('accessToken', accessToken);
                    console.log('access token stored');
                    window.location.replace(url);
                }
            } catch (error) {
                console.error('Sign up error:', error);
            }
        }


export async function signOut(login_url){
    supabaseClient = await getSupabaseClient();
    let { error } = supabaseClient.auth.signOut();
        // Handle the response from Supabase
        if (error) {
            console.error('Sign out error:', error);
        } else {
            localStorage.removeItem('accessToken');
            window.location.replace(login_url);
        }
  }
