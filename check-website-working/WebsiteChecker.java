import java.io.BufferedInputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Objects;

public class WebsiteChecker {

    public static boolean checkWebsite(String website_url, String content){
        try{
            URI uri =  new URI(website_url);
            HttpURLConnection connection = (HttpURLConnection)uri.toURL().openConnection();

            int code = connection.getResponseCode();
            String type = String.valueOf(connection.getHeaderFields().get("Content-Type"));

            System.out.println("Website response code: " + code);
            System.out.println("Website content-type: " + type);

            if(code != 200 || !Objects.equals(type, "[text/html]")){
                return false;
            }
            BufferedInputStream reader = new BufferedInputStream(connection.getInputStream());

            StringBuilder website= new StringBuilder();
            int count;
            byte[] buffer = new byte[1024];
            while( (count = reader.read(buffer)) != -1 ){
                website.append(new String(buffer, 0, count));
            }

            // System.out.println(website);

            if(!website.toString().contains(content)){
                return false;
            }

            return true;
        } catch (MalformedURLException e) {
            System.out.println("MalformedURLException raised!");
            throw new RuntimeException(e);
        } catch (IOException e) {
            System.out.println("IOException raised!");
            throw new RuntimeException(e);
        } catch (URISyntaxException e) {
            System.out.println("URISyntaxException raised!");
            throw new RuntimeException(e);
        }
    }

    public static void main(String[] args){
        String url = "http://th.if.uj.edu.pl";
        String neededTitle = "Institute of Theorethical Physics";

        boolean working = WebsiteChecker.checkWebsite(url, neededTitle);
        System.out.println(working ? "Website is working" : "Something is wrong");
        if(working)
            System.exit(0); // Sukces
        else
            System.exit(1); // Porażka
    }

}
