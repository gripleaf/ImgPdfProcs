package PdfWaterMark;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;

import com.itextpdf.text.Document;
import com.itextpdf.text.DocumentException;
import com.itextpdf.text.Image;
import com.itextpdf.text.PageSize;
import com.itextpdf.text.Rectangle;
import com.itextpdf.text.pdf.PdfContentByte;
import com.itextpdf.text.pdf.PdfImportedPage;
import com.itextpdf.text.pdf.PdfReader;
import com.itextpdf.text.pdf.PdfWriter;
import com.sun.xml.internal.bind.v2.runtime.unmarshaller.XsiNilLoader.Array;

public class Main {

	public static void ArgumentsTest(String[] args) {
		if (args.length != 3) {
			throw new IllegalArgumentException(
					"Argument lenght is not correct!");
		}
		for (int i = 0; i < 2; i++) {
			File f = new File(args[i]);
			if (!f.exists()) {
				throw new IllegalArgumentException(String.format(
						"%s is not exist.", args[i]));
			}
		}
	}

	/**
	 * @param infile
	 * @param oufile
	 * @return outfile
	 */
	public static String RotatePdfFile(String infile, String outfile)
			throws Exception {
		/**
		 * create reader & writer
		 */
		// the page size of new pdf document
		Rectangle pageSize;
		// document instance
		Document document;

		// initialize pdf reader
		PdfReader reader = new PdfReader(infile);
		// get the first page size

		Rectangle unitSize = reader.getPageSize(1);

		// create the page size of new document
		if (unitSize.getWidth() > unitSize.getHeight()) {
			pageSize = PageSize.A4.rotate();
		} else {
			pageSize = PageSize.A4;
		}

		document = new Document(pageSize);
		PdfWriter writer = PdfWriter.getInstance(document,
				new FileOutputStream(outfile));
		// initialize document
		document.open();
		PdfContentByte canvas = writer.getDirectContent();

		// initialize first page
		PdfImportedPage page = writer.getImportedPage(reader, 1);
		Image img = Image.getInstance(page);
		if (page.getRotation() % 100 == 90) {
			img.setRotationDegrees(360 - page.getRotation());
			document.setPageSize(reader.getPageSize(1).rotate());
		} else {
			document.setPageSize(reader.getPageSize(1));
		}

		document.add(img);
		document.newPage();

		for (int i = 1; i <= reader.getNumberOfPages(); i++) {
			page = writer.getImportedPage(reader, i);
			img = Image.getInstance(page);
			img.setAbsolutePosition(0, 0);
			if (page.getRotation() % 100 == 90) {
				img.setRotationDegrees(360 - page.getRotation());
				if (i + 1 <= reader.getNumberOfPages())
					document.setPageSize(reader.getPageSize(i + 1).rotate());
			} else {
				if (i + 1 <= reader.getNumberOfPages())
					document.setPageSize(reader.getPageSize(i + 1));
			}

			canvas.addImage(img);
			document.newPage();
		}
		document.close();
		System.out.println("rotate done!");
		return outfile;
	}

	/**
	 * @param argv
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {
		// System.out.println("Usage: xx.jar input image output");
		ArgumentsTest(args);

		String infile = args[0];
		String img_path = args[1];
		String outfile = args[2];
		/*
		 * String infile = "C:\\Users\\gripleaf\\Desktop\\inputx.pdf"; String
		 * img_path = "C:\\Users\\gripleaf\\Desktop\\watermark.png"; String
		 * outfile = "C:\\Users\\gripleaf\\Desktop\\err_out.pdf";
		 */
		/**
		 * create reader & writer
		 */
		// the page size of new pdf document
		Rectangle pageSize;
		// document instance
		Document document;

		// initialize pdf reader
		PdfReader reader = new PdfReader(infile);

		// a empty pdf
		if (reader.getNumberOfPages() == 0) {
			throw new NullPointerException(String.format("%s is a empty pdf.",
					infile));
		}

		// get the first page size
		Rectangle unitSize = reader.getPageSize(1);

		// create the page size of new document
		if (unitSize.getWidth() > unitSize.getHeight()) {
			pageSize = PageSize.A4.rotate();
		} else {
			pageSize = PageSize.A4;
		}

		if (reader.getPageRotation(1) % 180 == 90) {
			unitSize = unitSize.rotate();
			pageSize = pageSize.rotate();
		}

		document = new Document(pageSize);
		PdfWriter writer = PdfWriter.getInstance(document,
				new FileOutputStream(outfile));
		// initialize document
		document.open();
		PdfContentByte canvas = writer.getDirectContent();
		PdfImportedPage page;

		/**
		 * Create Image
		 */
		Image image = Image.getInstance(img_path);
		image.setAbsolutePosition(0, 0);
		image.scalePercent(pageSize.getWidth() / image.getWidth() * 100f);

		for (int i = 1; i <= reader.getNumberOfPages(); i++) {
			page = writer.getImportedPage(reader, i);
			float factor = Math.min(pageSize.getWidth() / unitSize.getWidth(),
					pageSize.getHeight() / unitSize.getHeight());

			if (i + 1 <= reader.getNumberOfPages()) {
				unitSize = reader.getPageSize(1);

				// create the page size of new document
				if (unitSize.getWidth() > unitSize.getHeight()) {
					pageSize = PageSize.A4.rotate();
				} else {
					pageSize = PageSize.A4;
				}

				if (page.getRotation() % 100 == 90) {
					unitSize = unitSize.rotate();
					pageSize = pageSize.rotate();
				}

				document.setPageSize(pageSize);
			}

			/*
			 * // offsetX∫ÕoffsetY…Ë÷√ float offsetX = page.getWidth() +
			 * (page.getWidth() - (PageSize.A4.getHeight() * factor)) / 2f;
			 * float offsetY = page.getHeight() + (page.getHeight() -
			 * (PageSize.A4.getWidth() * factor)) / 2f;
			 */
			// canvas.addTemplate(page, factor, 0, 0, factor, 0, 0);
			Image img = Image.getInstance(page);
			img.setAbsolutePosition(0, 0);
			img.scalePercent(factor * 100.0f);
			img.setRotationDegrees(360 - page.getRotation());
			canvas.addImage(img);
			canvas.addImage(image);
			document.newPage();
		}
		document.close();
		System.out.println("convert done!");
	}
}
