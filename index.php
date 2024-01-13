<?php
require_once('HaremAltin.php');
$haremAltin = new HaremAltin();

/**  
	Tüm verileri çekmek için kullanılır.
**/

$data = $haremAltin->getAllCurrency();
print_r($data);

/**  
	Döviz kodunu girerek verileri çekebilirsiniz.
	Örnek:
	$haremAltin->getCurrency('USDTRY');
	$haremAltin->getCurrency('EURTRY');
	
	Object
	$usdTry = $haremAltin->getCurrency('USDTRY');
	print_r($usdTry);
	$code = $usdTry->code;			//Parite
	$alis = $usdTry->alis;			//Alış
	$satis = $usdTry->satis;		//Satış
	$tarih = $usdTry->tarih;		//Tarih
	$dusuk = $usdTry->dusuk;		//En düşük
	$yuksek = $usdTry->yuksek;		//En yüksek
	$kapanis = $usdTry->kapanis;	//Kapanış
**/

$usdTry = $haremAltin->getCurrency('USDTRY');
print_r($usdTry);
?>