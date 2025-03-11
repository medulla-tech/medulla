<?php
/*
/!\ Warning:

The \Core\Request Object needs a SERVER context. It implies GET, POST, HEADERS ... which are not loaded for this tests
*/

$_GET['debug'] = true;
$_GET['uri'] = 'phpunit/unittest';
$_POST['posted'] = 'unitest';

class RequestTest extends \PHPUnit\Framework\TestCase{

    public function testPrivateConstructor(){
        $this->expectExceptionMessage('Call to protected');
        new \Core\Request();
    }

    public function testIsRequestSingleton(){
        $req = \Core\Request::getInstance();
        $req2 = \Core\Request::getInstance();

        $this->assertEquals($req, $req2);
    }

    /**
     * Test the hasConfig method on different senario
     */
    public function testHasConfigWithoutParameter(){
        $req = \Core\Request::getInstance();
        $this->assertFalse($req->hasConfig(""));

        $this->expectExceptionMessage("Too few arguments to function");
        $this->assertFalse($req->hasConfig());
    }

    public function testHasConfig(){
        $req = \Core\Request::getInstance();
        //     "protocol"=>(!empty($_SERVER["REQUEST_SCHEME"])) ? htmlentities($_SERVER["REQUEST_SCHEME"]) : "http",
        $this->assertTrue($req->hasConfig("protocol"));

        //     "dns"=>(!empty($_SERVER["HTTP_HOST"])) ? htmlentities($_SERVER["HTTP_HOST"]) : "",
        $this->assertTrue($req->hasConfig("dns"));

        //     "port"=>(!empty($_SERVER["SERVER_PORT"])) ? htmlentities($_SERVER["SERVER_PORT"]) : 80,
        $this->assertTrue($req->hasConfig("port"));

        //     "prefix"=>!empty($_SERVER["CONTEXT_PREFIX"]) ? htmlentities($_SERVER["CONTEXT_PREFIX"]) : "",
        $this->assertTrue($req->hasConfig("prefix"));

        //     "client"=>!empty($_SERVER["HTTP_USER_AGENT"]) ? htmlentities($_SERVER["HTTP_USER_AGENT"]): "none",
        $this->assertTrue($req->hasConfig("client"));

        //     "uri"=>$uri,
        $this->assertFalse($req->hasConfig("unknown"));

        //     "client-ip"=>!empty($_SERVER['REMOTE_ADDR']) ? htmlentities($_SERVER["REMOTE_ADDR"]) : '',
        $this->assertTrue($req->hasConfig("client-ip"));

    }

    public function testConfigWithoutParam(){
        $req = \Core\Request::getInstance();

        $this->assertIsArray($req->config());
        $this->assertIsArray($req->config(""));
    }

    public function testConfigWithKey(){
        $req = \Core\Request::getInstance();

        $this->assertEquals($req->config("protocol"), "http");
        $this->assertEquals($req->config("dns"), "");
        $this->assertEquals($req->config("port"), 80);
        $this->assertEquals($req->config("prefix"), "");
        $this->assertEquals($req->config("client"), "none");
        $this->assertEquals($req->config("uri"), "phpunit/unittest");
        $this->assertEquals($req->config("unknown"), NULL);
    }

    public function testConfigWithKeyValue(){
        $req = \Core\Request::getInstance();

        $oldValue = $req->config("test", "unittest");
        $this->assertNULL($oldValue);

        $oldValue = $req->config("test", "new unittest");
        $this->assertIsString($oldValue);
        $this->assertEquals($oldValue, "unittest");

        $oldValue2 = $req->config("test", "new unittest2");
        $this->assertIsString($oldValue2);

        $this->assertEquals($oldValue2, "new unittest");
        $this->assertEquals($req->config("test"), "new unittest2");
    }



    public function testHasHeaderWithoutParams(){
        $req = \Core\Request::getInstance();
        $this->expectExceptionMessage("Too few arguments to function");
        $this->assertFalse($req->hasHeader());
    }

    public function testHasHeader(){
        $req = \Core\Request::getInstance();
        $this->assertFalse($req->hasHeader("unknown"));
    }

    public function testheader(){
        $req = \Core\Request::getInstance();
        $this->assertIsArray($req->header());

        $this->assertEquals($req->header("unknown"), "");
    }

    public function testHasGetWithoutParams(){
        $req = \Core\Request::getInstance();
        $this->expectExceptionMessage("Too few arguments to function");
        $this->assertFalse($req->hasGet());
    }

    public function testHasGet(){
        $req = \Core\Request::getInstance();

        $this->assertFalse($req->hasGet('uri'));
        $this->assertTrue($req->hasGet('debug'));
        $this->assertFalse($req->hasGet("unknown"));
    }

    public function testGet(){
        $req = \Core\Request::getInstance();
        $this->assertIsArray($req->get());
        $this->assertNULL($req->get("unknown"));
        $this->assertEquals($req->get("debug"), true);
    }

    public function testHasPostWithoutParams(){
        $req = \Core\Request::getInstance();
        $this->expectExceptionMessage("Too few arguments to function");
        $this->assertFalse($req->hasPost());
    }

    public function testHasPost(){
        $req = \Core\Request::getInstance();
        $this->assertTrue($req->hasPost('posted'));
        $this->assertFalse($req->hasPost('unknown'));
    }

    public function testPost(){
        $req = \Core\Request::getInstance();
        $this->assertEquals($req->post("posted"), "unitest");
        $this->assertNULL($req->post("unknown"));
    }
};
?>
